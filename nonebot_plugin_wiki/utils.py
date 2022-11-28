"""
将消息转化为Nonebot的可发送对象
"""

from typing import Union

from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters import Message

from .SubCmd.utils import set_wiki
from .mediawiki import wikipedia as wiki
from .data import MWiki
from .mediawiki.exceptions import NoExtractError

from . import handle

global PROXIES


def set_proxies(raw_mwiki, proxies=dict()):
    global PROXIES

    PROXIES = (proxies or raw_mwiki)


def reply_out(msg_id: int, output: str) -> Message:
    """给消息包装上“回复”

    Args:
        msg_id (int): 所要回复的消息id
        output (str): 所要包装的消息原文

    Returns:
        Message
    """
    return MessageSegment.reply(id_=msg_id) + MessageSegment.text(output)


# TODO
# ! 目前重定向可能会出现完全不相干的结果返回
async def output(
    title: str,
    mwiki: MWiki,
    msg_id: int = int(),
    auto_suggest=True,
    redirect=True,
    has_title=False,
) -> Union[str, Message]:
    """将输入的标题转化为格式化的消息

    Args:
        title (str): 页面标题
        mwiki (MWiki): MWik对象 Defaults to RAW_MWIKI.
        msg_id (int): 所“回复”的消息id Defaults to int().
        auto_suggest (bool, optional): 是否启用自动建议 Defaults to True.
        redirect (bool, optional): 是否接受自动重定向 Defaults to True.
        has_title (bool, optional): 消息内是否再次注明标题 Defaults to False.

    Returns:
        Union[str, Message]
    """
    # 大型赋值现场
    set_wiki(mwiki, PROXIES)

    try:
        curid, _summary = await wiki.summary(
            title, auto_suggest=auto_suggest, redirect=redirect
        )

    except NoExtractError:
        return reply_out(msg_id, '目标wiki不支持生成简介')
    except wiki.ApiReturnError:
        return reply_out(msg_id, 'api多次返回异常，请检查api状态或稍后重试')
    except wiki.PageError:
        return reply_out(msg_id, '目标页面不存在')
    except wiki.DisambiguationError as DE:
        raise DE
    except wiki.WikipediaException as e:
        return reply_out(msg_id, f'未知错误：{e}')

    _summary = handle.nn_to_n(handle.chars_max(
        _summary, max=200))  # type: ignore

    out = (
        (f'「{title}」\n' if has_title else '')
        + f'{wiki.get_curid_url()}{curid}\n'
        + f'{_summary}'
    )

    return reply_out(msg_id, out) if msg_id else out
