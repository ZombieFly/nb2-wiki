import re
import json
from typing import Tuple

from .data import Data, MWiki


#* 文字处理部分
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

    def chars_max(self, txt='', max=0) -> str:
        '''
        控制输入文本最大字数,并在末尾追加省略信息
        '''
        txt = (self.raw if not txt else txt)
        return  (txt if len(txt) <= max or not max else txt[:max] + f'……\n[字数大于{max}字部分被省略]')

#* 子命令
class Cmd:
    @classmethod
    def add(self, args):
        """#增加记录

        Args:
            args (dict): 传入参数

        Returns:
            str: 执行结果
        """        
        fn_args = args['fn_args']
        url = (fn_args[1] if fn_args[1][-1] == r'/' else fn_args[1]+r'/')
        Data().add_wiki(
            MWiki(name=fn_args[0],
                    api_url=url+'api.php',
                    curid_url=url+'index.php?curid=',
                    need_proxy=False),
            args['group_id'],
        )
        
        return '记录完成'

    @classmethod
    def rm(self, args) -> str:
        Data().remove_wiki(args['fn_args'][0], args['group_id'])

        return "移除wiki成功！"

    @classmethod
    def list(self, args):
        wiki_list = Data().get_wiki_list(args['group_id'])

        if wiki_list:
            result = "本群wiki记录列表如下：\n" + "\n".join(
                f"[{wiki.name}]{wiki.api_url[:-8]}"
                for wiki in wiki_list
            )
        else:
            result = "本群wiki记录为空"

        return result

    @classmethod
    def select_mwiki(self, wiki_name:str, group_id:int) -> Tuple[MWiki, None]:
        """
        获得已记录的MWiki对象
        不存在时返回None

        Args:
            wiki_name (str): wiki记录名称
            group_id (int): 群id

        Returns:
            MWiki | None
        """        
        wiki_list = Data().get_wiki_list(group_id)
        if wiki_name in (
            wiki.name
            for wiki in wiki_list
                        ):
            __wiki = MWiki()
            for wiki in wiki_list:
                if wiki_name == wiki.name:
                    __wiki = wiki
            return __wiki
        else:
            #* 不存在对应wiki配置
            return None

    @classmethod
    def demo(self, args: dict):
        return json.dumps(args)