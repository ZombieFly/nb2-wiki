"""
用以处理简介、搜索结果输出
"""

from typing import List
import re

from . import mediawiki as Wiki


def nn_to_n(raw: str) -> str:
    '''
    将文本中的两个回车替换为一个回车
    '''
    return re.sub(r"\n\n", r"\n", raw)


def refer_to_list(raw: Wiki.exceptions.DisambiguationError, max: int = 10) -> List[str]:
    """将建议列表以列表形式输出,参数max控制返回列表最大长度

    Args:
        raw (Wiki.exceptions.DisambiguationError): DisambiguationError类
        max (int, optional): 列表最大长度. Defaults to 10.

    Returns:
        list: 结果列表
    """
    ret: list = raw.options
    return ret if (max >= len(ret) or not max) else ret[:max]


def chars_max(raw: str, txt=str(), max=0) -> str:
    '''
    控制输入文本最大字数,并在末尾追加省略信息
    '''
    txt = (txt or raw)
    return (
        txt
        if len(txt) <= max or not max else
        txt[:max] + f'……\n[字数大于{max}字部分被省略]'
    )
