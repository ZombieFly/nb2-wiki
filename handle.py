import re
from urllib.parse import quote

from . import mediawiki as wiki

class Handle:
    '''
    用以处理简介、搜索结果输出
    '''
    def __init__(self, raw: str) -> None:
        self.raw:str = raw

    def nn_to_n(self) -> str:
        '''
        将文本中的两个回车替换为一个回车
        '''
        return re.sub(r"\n\n", r"\n", self.raw)

    def refer_to_list(self, max:int=0) -> list:
        '''
        将建议列表以列表形式输出,参数max控制返回列表最大长度
        '''
        ret = self.raw.options
        return ret if (max >= len(ret) or not max) else ret[:max]

    def title_to_url(self, txt='', url_head=wiki.WIKI_URL):
        '''
        通过标题编码为url形式
        '''
        txt = (self.raw if not txt else txt)
        return f'{url_head}/{quote(txt)}'

    def chars_max(self, txt='', max=0) -> str:
        '''
        控制输入文本最大字数,并在末尾追加省略信息
        '''
        txt = (self.raw if not txt else txt)
        return  (txt if len(txt) <= max or not max else txt[:max] + f'……\n[字数大于{max}字部分被省略]')
