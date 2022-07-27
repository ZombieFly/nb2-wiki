"""
用以处理简介、搜索结果输出
"""

import re

from . import mediawiki as Wiki


def nn_to_n(raw: str) -> str:
    '''
    将文本中的两个回车替换为一个回车
    '''
    return re.sub(r"\n\n", r"\n", raw)


def refer_to_list(raw: Wiki.exceptions.DisambiguationError, max: int = 0) -> list:
    '''
    将建议列表以列表形式输出,参数max控制返回列表最大长度
    '''
    ret: list = raw.options  # type: ignore
    return ret if (max >= len(ret) or not max) else ret[:max]


def chars_max(raw: str, txt='', max=0) -> str:
    '''
    控制输入文本最大字数,并在末尾追加省略信息
    '''
    txt = (raw if not txt else txt)
    return (
        txt
        if len(txt) <= max or not max else
        txt[:max] + f'……\n[字数大于{max}字部分被省略]'
    )
