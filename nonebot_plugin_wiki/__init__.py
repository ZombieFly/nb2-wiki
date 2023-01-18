from typing import Dict, cast, NoReturn
import contextlib
import traceback

from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent
from nonebot.exception import RejectedException, FinishedException
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot import get_driver, on_command
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot.adapters import Bot
from nonebot.log import logger

from .utils import output, reply_out, set_proxies
from .SubCmd.utils import select_mwiki
from .SubCmd import admin, member
from .config import Config
from .data import MWiki
from . import handle

from . import mediawiki as wiki


global_config = get_driver().config
config = Config.parse_obj(global_config)


PROXIES = config.proxies
REFER_MAX = config.refer_max
CMD_START = config.cmd_start
wiki.set_retry_times(config.retry_times)

RAW_MWIKI = MWiki()

for _key, _value in cast(Dict, config.raw_mwiki).items():
    setattr(RAW_MWIKI, _key, _value)


config.raw_mwiki = RAW_MWIKI

set_proxies(PROXIES, RAW_MWIKI)

cmd = on_command(CMD_START[0], aliases=set(CMD_START[1:]), permission=GROUP)

CMD_START = [f'{i} ' for i in CMD_START]
search = on_command(CMD_START[0], aliases=set(CMD_START[1:]))


###################################################################

async def handle_opt(bot: Bot, state: T_State, numb: str, msg_id: int) -> NoReturn:
    """条目标号处理

    Args:
        bot (Bot): Bot实例
        state (T_State): 会话状态
        numb (str): 用户输入的标号
        msg_id (int): 标号消息ID

    Raises:
        FinishedException: 会话结束
    """

    # * 撤回搜索结果列表消息
    await bot.delete_msg(message_id=state['refer_msg_id']['message_id'])
    try:
        numb = int(numb)  # type: ignore
        logger.debug(f'用户输入的标号是{numb}')
        outstr = await output(
            title=state['results'][numb],
            mwiki=state['mwiki'] if state.__contains__(
                'mwiki') else RAW_MWIKI,
            msg_id=msg_id,
            has_title=True
        )

        await search.send(outstr)
    except ValueError:
        # 输入的非数字时的处理
        await search.send('取消搜索')
    except IndexError:
        # 给的数字超出了索引时的处理
        await search.send(f'{numb}超出了索引')
    raise FinishedException


async def handle_first(state: T_State, keywd: str, msg_id: int) -> NoReturn:
    """处理第一次搜索

    Args:
        state (T_State): 会话状态
        keywd (str): 用户输入的关键词
        msg_id (int): 消息ID

    Raises:
        RejectedException: 重开会话，等待用户输入条目标号
    """

    try:
        # * 有直接对应的页面
        outstr = await output(title=keywd, mwiki=state['mwiki'] if state.__contains__('mwiki') else RAW_MWIKI, redirect=True, msg_id=msg_id)

        await search.finish(outstr)
    except wiki.exceptions.DisambiguationError as DE:
        # * 没有对应页面，但可生成相似结果列表
        state['results'] = handle.refer_to_list(raw=DE, max=REFER_MAX)
        out = (
            '有关结果如下，输入对应标号发起搜索，回复其他字符自动取消:\n' +
            '\n'.join(
                f'[{n}]{state["results"][n]}'
                for n in range(len(state["results"]))
            ) +
            (f'\n(仅展示前{REFER_MAX}个结果)'
             if (len(state["results"]) > REFER_MAX) else
             '')
        )
        out = reply_out(msg_id=msg_id, output=out)
        state['refer_msg_id'] = await search.send(out)
        raise RejectedException from DE
    except wiki.exceptions.PageError:
        # * 没有任何相关条目
        await search.finish(reply_out(output='没有找到任何相关结果', msg_id=msg_id))


async def search_from_another_wiki(
    bot: Bot,
    event: GroupMessageEvent,
    state: T_State,
    args: dict,
    wiki_name: str
):
    """从已记录的wiki中寻找对应的wiki搜索

    Args:
        bot (Bot): Bot实例
        event (GroupMessageEvent): 群聊事件
        state (T_State)
        args (dict): 传入的参数
        wiki_name (str): wiki名称
    """
    state['mwiki'] = await select_mwiki(
        wiki_name, args['group_id']
    )
    if state['mwiki']:
        try:
            logger.debug(
                f'[S4]已记录wiki"{state["mwiki"].name}"被找到，尝试开始调用搜索，'
                + f'搜索关键词为<{" ".join(args["fn_args"])}>'
            )
            await _search(bot, event, state, " ".join(args["fn_args"]))
        except IndexError:
            logger.debug(
                f'[S5]已记录wiki"{state["mwiki"].name}"被找到，但不存在关键词')
    else:
        await cmd.finish(
            reply_out(
                event.message_id,
                '不存在的命令或是已记录wiki，请检查是否具有对应权限或者输入是否正确'
            )
        )


async def run_cmd(event: GroupMessageEvent, args: dict, cmd_name: str):
    """执行子命令

    Args:
        event (GroupMessageEvent)
        args (dict): 传入的参数
        cmd_name (str): 子命令名称

    Raises:
        AttributeError: _description_
    """
    try:
        # * 优先尝试普通权限命令
        await cmd.send(
            reply_out(
                event.message_id,
                await getattr(member, cmd_name)(args)
            )
        )
        logger.debug(f"[S1M]找到并执行了普通权限命令{cmd_name}")
    except AttributeError as err:
        logger.debug(
            f'[S1]执行普通权限命令触发异常<{repr(err)}>，逻辑为未寻找到普通权限命令"{cmd_name}"'
        )
        if event.sender.role not in ['admin', 'owner']:
            # * 普通成员调用不存在的平级命令或是管理员权限命令
            raise AttributeError from err
            # * 管理员及群主会再尝试执行管理员级命令
        await cmd.send(
            reply_out(
                event.message_id,
                await getattr(admin, cmd_name)(args)
            )
        )
        logger.debug(f"[S2]找到并执行了管理员级命令{cmd_name}")
    except Exception as e:
        logger.debug(
            f'[S2M]触发意料外的异常:\n{traceback.format_exc()}')
        await cmd.finish(reply_out(event.message_id, f'发生异常：\n{repr(e)}'))

###################################################################


@search.handle()
async def _search(
    bot: Bot, event: MessageEvent, state: T_State, keywd=CommandArg()
):
    with contextlib.suppress(Exception):
        # 子命令功能在个人会话中禁用，故此处实为个人会话直接调用搜索
        keywd = keywd.extract_plain_text()
    numb: str = event.message.extract_plain_text()
    msg_id = event.message_id

    if numb and not keywd:
        # * 用户发送了对应条目的标号后的处理
        await handle_opt(bot, state, numb, msg_id)

    else:
        # * 会话开启的第一次处理
        await handle_first(state, keywd, msg_id)


@cmd.handle()
async def _cmd(
    bot: Bot, event: GroupMessageEvent, state: T_State, keywd=CommandArg()
):
    args = {'group_id': event.group_id, 'config': config}

    try:
        keywd = keywd.extract_plain_text()
    except AttributeError:
        await _search(bot, event, state, keywd)
    else:

        if not keywd:
            # TODO 接入帮助
            logger.debug("无参数追加，不进行处理")

        if keywd[0] in get_driver().config.command_start:
            # 解析出子命令与参数
            to_run, *args['fn_args'] = keywd[1:].split()
            logger.debug(f"[S0]主参数为<{to_run}>，追加参数为<{args}>")
            try:
                # * 尝试执行子命令
                await run_cmd(event, args, to_run)
            except AttributeError:
                logger.debug(f'[S3]子命令"{to_run}"未找到，尝试从已记录wiki中寻找')
                await search_from_another_wiki(bot, event, state, args, to_run)
            except Exception as e:
                logger.debug(f'[S6]触发意料外的异常:\n{traceback.format_exc()}')
                await cmd.finish(reply_out(event.message_id, f'发生异常：\n{repr(e)}'))
