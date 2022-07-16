from nonebot import get_driver, on_command
from nonebot.adapters import Bot
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    MessageSegment,
    GroupMessageEvent
)
from nonebot.exception import RejectedException, FinishedException
from nonebot.adapters.onebot.v11.permission import GROUP

from .config import Config

from . import mediawiki as wiki

from .data import MWiki

from .handle import Cmd_admin, Cmd_member, Handle

global_config = get_driver().config
config = Config.parse_obj(global_config)

#* 初始MWiki
raw_MWiki = MWiki(
    name= 'mc',
    api_url= 'Https://minecraft.fandom.com/zh/api.php',
    curid_url= 'https://minecraft.fandom.com/zh/index.php?curid=',
    user_agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
    need_proxy= False
)


PROXIES = config.proxies
#api_url = 'https://mobile.moegirl.org.cn/api.php'
#wiki.set_api_url('https://minecraft.fandom.com/zh/api.php')
#wiki.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36')
#USER_AGENT = 'Mozilla/5.0 (Linux; Android 12; SM-F9160 Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/102.0.5005.78 Mobile Safari/537.36'
#wiki.set_curid_url('')
#CURID_URL = 'https://zh.moegirl.org.cn/index?curid='
refer_max = 10
cmd_start = ['wiki', '维基']


cmd = on_command(cmd_start[0], aliases= set(cmd_start), permission=GROUP)

cmd_start = [i+' ' for i in cmd_start]
search = on_command(cmd_start[0], aliases= set(cmd_start[1:]))

###################################################################

def reply_out(msg_id:int, output:str) -> list[MessageSegment]:
    """给消息包装上“回复”

    Args:
        msg_id (int): 所要回复的消息id
        output (str): 所要包装的消息原文

    Returns:
        list[MessageSegment]
    """
    return MessageSegment.reply(id_=msg_id) + MessageSegment.text(output)

# TODO
# ! 目前重定向可能会出现完全不相干的结果返回
async def output(
    title: str,
    mwiki: MWiki= raw_MWiki,
    auto_suggest= True,
    redirect= True,
    is_reply= False,
    has_title= False,
    msg_id:int= None,
) -> str:
    """将输入的标题转化为格式化的消息

    Args:
        title (str): 页面标题
        mwiki (MWiki): MWik对象 
        auto_suggest (bool, optional): 是否启用自动建议 Defaults to True.
        redirect (bool, optional): 是否接受自动重定向 Defaults to True.
        is_reply (bool, optional): 所发送的消息是否“回复” Defaults to False.
        has_title (bool, optional): 消息内是否再次注明标题 Defaults to False.
        msg_id (int, optional): 所“回复”的消息id Defaults to None.

    Returns:
        str
    """
    #大型赋值现场
    wiki.set_api_url(mwiki.api_url)
    #todo
    #! 此处curid_url无法正常赋值
    wiki.set_curid_url(mwiki.curid_url)
    wiki.set_user_agent(raw_MWiki.user_agent if not mwiki.user_agent else mwiki.user_agent)
    wiki.set_proxies(PROXIES if mwiki.need_proxy else {})

    curid, _summary = await wiki.summary(title, auto_suggest= auto_suggest, redirect= redirect)

    _summary = Handle(Handle(_summary).chars_max(max=200)).nn_to_n()
    out = (
        (f'「{title}」\n' if has_title else '')
        +f'{wiki.get_curid_url()}{curid}\n'
        +f'{_summary}'
    )
    return out if is_reply and not msg_id else reply_out(msg_id, out)

###################################################################

@search.handle()
async def _search(bot: Bot, event: GroupMessageEvent, state: T_State, keywd= CommandArg()):
    try:
        #直接调用搜索
        keywd = keywd.extract_plain_text()
    except:
        #通过Cmd子命令调用
        pass

    numb:str = event.message.extract_plain_text()
    msg_id = event.message_id
    if numb and not keywd:
        # * 用户发送了对应条目的标号后的处理
        # * 撤回搜索结果列表消息
        await bot.delete_msg(message_id=state['refer_msg_id']['message_id'])
        try:
            numb = int(numb)
            outstr = await output(title=state['results'][numb],
                                mwiki= (raw_MWiki if not state.__contains__('mwiki') else state['mwiki']),
                                msg_id= msg_id,
                                is_reply= True,
                                has_title= True)
                  
            await search.send(outstr)
        except ValueError:
            #输入的非数字时的处理
            await search.send('取消搜索')
        except IndexError:
            #给的数大了
            await search.send(f'{numb}超出了索引')
        raise FinishedException

    else:
        # * 会话开启的第一次处理
        try:
            # * 有直接对应的页面
                outstr = await output(title= keywd,
                                    mwiki= (raw_MWiki if not state.__contains__('mwiki') else state['mwiki']),
                                    redirect= True,
                                    msg_id= msg_id, 
                                    is_reply= True)
                await search.finish(outstr)
        except wiki.exceptions.DisambiguationError as msg:
            # * 没有对应页面，但可生成相似结果列表
            state['results'] = Handle(msg).refer_to_list(max=refer_max)
            out = ('有关结果如下，输入对应标号发起搜索，回复其他字符自动取消:\n'+
                   '\n'.join(
                    f'[{n}]{state["results"][n]}'
                    for n in range(len(state["results"]))
                    )
                    +(f'\n(仅展示前{refer_max}个结果)' if (len(state["results"]) > refer_max) else '')
            )
            out = reply_out(msg_id=msg_id, output=out)
            state['refer_msg_id'] = await search.send(out)
            raise RejectedException
        except wiki.exceptions.PageError:
            # * 没有任何相关条目
            await search.finish(reply_out(output='没有找到任何相关结果', msg_id=msg_id))

@cmd.handle()
async def _cmd(bot:Bot, event: GroupMessageEvent,state: T_State, keywd= CommandArg()):
    args = dict()
    args['group_id'] = event.group_id
    try:
        keywd = keywd.extract_plain_text()
    except AttributeError:
        await _search(bot, event, state, keywd)
    else: 
        if keywd[0] in get_driver().config.command_start:
            #解析出子命令与参数
            keywd = keywd[1:].split()
            args['fn_args'] = keywd[1:]
            try:
                #* 尝试执行子命令
                try:
                    #* 优先尝试普通权限命令
                    await cmd.send(reply_out(event.message_id, await getattr(Cmd_member, keywd[0])(args)))
                except AttributeError:
                    raise AttributeError
                except:
                    #? 这里捕获了所有的异常，或许没法处理执行出现异常的平级命令
                    #* 平级命令执行错误（大概率是没这个平级命令）
                    if event.sender.role in ['admin', 'owner']:
                        #* 管理员及群主会再尝试执行管理员级命令
                        await cmd.send(reply_out(event.message_id, await getattr(Cmd_admin, keywd[0])(args)))
                    else:
                        #* 普通成员调用不存在的平级命令或是管理员权限命令
                        await cmd.finish(reply_out(event.message_id, '不存在的命令，或者您没有足够的权限执行'))
            except AttributeError:
                #* 不存在对应子命令时，调用seletc_wiki函数，获取可能的对应的wiki配置
                #传入MWiki类
                state['mwiki'] = await Cmd_member.select_mwiki(keywd[0], args['group_id'])
                if state['mwiki']:
                    await _search(bot, event, state, keywd)
                else:
                    await cmd.finish(reply_out(event.message_id, '不存在的命令或是已记录wiki，请检查是否具有对应权限或者输入是否正确'))
            except Exception as err:
                await cmd.finish(reply_out(event.message_id, str(err)))
