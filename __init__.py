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

from .handle import Handle, Cmd

global_config = get_driver().config
config = Config.parse_obj(global_config)

wiki.set_proxies({'All://':'http://127.0.0.1:10809'})
wiki.set_api_url('https://mobile.moegirl.org.cn/api.php')
#wiki.set_api_url('https://minecraft.fandom.com/zh/api.php')
#wiki.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36')
wiki.set_user_agent('Mozilla/5.0 (Linux; Android 12; SM-F9160 Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/102.0.5005.78 Mobile Safari/537.36')
#wiki.set_curid_url('https://minecraft.fandom.com/zh/index.php?curid=')
CURID_URL = 'https://zh.moegirl.org.cn/index?curid='
refer_max = 10
cmd_start = ['wiki', '维基']


cmd = on_command(cmd_start[0], aliases= set(cmd_start), permission=GROUP)

cmd_start = [i+' ' for i in cmd_start]
search = on_command(cmd_start[0], aliases= set(cmd_start[1:]))

###################################################################

def reply_out(msg_id:int, output:str) -> str:
    """给消息包装上“回复“

    Args:
        msg_id (int): 所要回复的消息id
        output (str): 所要包装的消息原文

    Returns:
        str
    """
    return MessageSegment.reply(id_=msg_id) + MessageSegment.text(output)

# TODO
# ! 目前重定向可能会出现完全不相干的结果返回
async def output(
    title: str,
    auto_suggest= True,
    redirect= True,
    is_reply= False,
    has_title= False,
    msg_id:int= None,
) -> str:
    """将输入的标题转化为格式化的消息

    Args:
        title (str): 页面标题
        auto_suggest (bool, optional): 是否启用自动建议 Defaults to True.
        redirect (bool, optional): 是否接受自动重定向 Defaults to True.
        is_reply (bool, optional): 所发送的消息是否“回复” Defaults to False.
        has_title (bool, optional): 消息内是否再次注明标题 Defaults to False.
        msg_id (int, optional): 所“回复”的消息id Defaults to None.

    Returns:
        str
    """
    summ = await wiki.summary(title, auto_suggest= auto_suggest, redirect= redirect)
    result = [title, summ[0], Handle(summ[1]).chars_max(max=200)]
    out = (
        (f'「{title}」\n' if has_title else '')
        +f'{CURID_URL}{result[1]}\n'
        +f'{result[2]}'
    )
    return out if is_reply and not msg_id else reply_out(msg_id, out)

###################################################################

@cmd.handle()
async def _(event, keywd= CommandArg()):
    keywd = keywd.extract_plain_text()
    args = dict()
    args['group_id'] = event.group_id
    if keywd[0] in get_driver().config.command_start:
        keywd = keywd[1:].split()
        args['fn_args'] = keywd[1:]
        try:
            await cmd.send(getattr(Cmd, keywd[0])(args))
        except AttributeError:
            __wiki = getattr(Cmd, 'select_wiki')(keywd[0], args['group_id'])
            wiki.API_URL = __wiki['api_url']
            wiki.CURID_URL = __wiki['curid_url']
        except Exception as err:
            await cmd.finish(err)

@search.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State, keywd= CommandArg()):
    numb:str = event.message.extract_plain_text()
    msg_id = event.message_id
    if numb and not keywd:
        # * 用户发送了对应条目的标号后的处理
        # * 撤回搜索结果列表消息
        await bot.delete_msg(message_id=state['refer_msg_id']['message_id'])
        try:
            numb = int(numb)
            await search.send(await output(title=state['results'][numb], msg_id=msg_id, is_reply=True, has_title=True))
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
            await search.finish(await output(keywd.extract_plain_text(), redirect=True, msg_id=msg_id, is_reply=True))
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
        