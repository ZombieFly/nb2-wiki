from .config import Config
from nonebot import get_driver, on_command
from nonebot.adapters import Bot
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    MessageEvent
)
from nonebot.exception import RejectedException, FinishedException
from nonebot.adapters.onebot.v11.permission import GROUP
from nonebot.log import logger


import traceback

from . import mediawiki as wiki


from .SubCmd.utils import select_mwiki
from .SubCmd import admin, member
from . import handle
from.utils import output, reply_out


global_config = get_driver().config
config = Config.parse_obj(global_config)

REFER_MAX = config.REFER_MAX
RAW_MWIKI = config.RAW_MWIKI
CMD_START = config.CMD_START
wiki.set_retry_times(config.RETRY_TIMES)


cmd = on_command(CMD_START[0], aliases=set(CMD_START[1:]), permission=GROUP)

CMD_START = [i + ' ' for i in CMD_START]
search = on_command(CMD_START[0], aliases=set(CMD_START[1:]))


###################################################################


@search.handle()
async def _search(
    bot: Bot, event: MessageEvent, state: T_State, keywd=CommandArg()
):
    try:
        # 子命令功能在个人会话中禁用，故此处实为个人会话直接调用搜索
        keywd = keywd.extract_plain_text()
    except Exception:
        # 通过Cmd子命令调用
        pass

    numb: str = event.message.extract_plain_text()
    msg_id = event.message_id
    if numb and not keywd:
        # * 用户发送了对应条目的标号后的处理
        # * 撤回搜索结果列表消息
        await bot.delete_msg(message_id=state['refer_msg_id']['message_id'])
        try:
            numb = int(numb)  # type: ignore
            logger.debug(f'用户输入的标号是{str(numb)}')
            outstr = await output(
                title=state['results'][numb],
                mwiki=(
                    RAW_MWIKI
                    if not state.__contains__('mwiki')else
                    state['mwiki']
                ),
                msg_id=msg_id,
                has_title=True
            )
            await search.send(outstr)
        except ValueError:
            # 输入的非数字时的处理
            await search.send('取消搜索')
        except IndexError:
            # 给的数大了
            await search.send(f'{numb}超出了索引')
        raise FinishedException

    else:
        # * 会话开启的第一次处理
        try:
            # * 有直接对应的页面
            outstr = await output(
                title=keywd,
                mwiki=(
                    RAW_MWIKI
                    if not state.__contains__('mwiki') else
                    state['mwiki']
                ),
                redirect=True,
                msg_id=msg_id,
            )
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
            raise RejectedException
        except wiki.exceptions.PageError:
            # * 没有任何相关条目
            await search.finish(reply_out(output='没有找到任何相关结果', msg_id=msg_id))


@cmd.handle()
async def _cmd(
    bot: Bot, event: GroupMessageEvent, state: T_State, keywd=CommandArg()
):
    args = dict()
    args['group_id'] = event.group_id
    args['config'] = config

    try:
        keywd = keywd.extract_plain_text()
    except AttributeError:
        await _search(bot, event, state, keywd)
    else:
        if keywd[0] in get_driver().config.command_start:
            # 解析出子命令与参数
            to_run, *args['fn_args'] = keywd[1:].split()
            logger.debug(f"[S0]主参数为<{to_run}>，追加参数为<{str(args)}>")
            try:
                # * 尝试执行子命令
                try:
                    # * 优先尝试普通权限命令
                    await cmd.send(
                        reply_out(
                            event.message_id,
                            await getattr(member, to_run)(args)
                        )
                    )
                    logger.debug(f"[S1M]找到并执行了普通权限命令{to_run}")
                except AttributeError as err:
                    logger.debug(
                        f'[S1]执行普通权限命令触发异常<{repr(err)}>，逻辑为未寻找到普通权限命令"{to_run}"'
                    )
                    if event.sender.role in ['admin', 'owner']:
                        # * 管理员及群主会再尝试执行管理员级命令
                        await cmd.send(
                            reply_out(
                                event.message_id,
                                await getattr(admin, to_run)(args)
                            )
                        )
                        logger.debug(f"[S2]找到并执行了管理员级命令{to_run}")
                    else:
                        # * 普通成员调用不存在的平级命令或是管理员权限命令
                        raise AttributeError
                except Exception:
                    logger.debug(
                        f'[S2M]触发意料外的异常:\n{traceback.format_exc()}')
                    await cmd.finish(reply_out(event.message_id, traceback.format_exc()))
            except AttributeError:
                logger.debug(f'[S3]子命令"{to_run}"未找到，尝试从已记录wiki中寻找')
                # * 不存在对应子命令时，调用seletc_wiki函数，获取可能的对应的wiki配置
                # 传入MWiki类
                state['mwiki'] = await select_mwiki(
                    to_run, args['group_id']
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
            except Exception:
                logger.debug(f'[S6]触发意料外的异常:\n{traceback.format_exc()}')
                await cmd.finish(reply_out(event.message_id, traceback.format_exc()))
