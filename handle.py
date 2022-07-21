import re
import json
from typing import Optional

from .data import Data, MWiki

from . import mediawiki as wiki

from .config import Config


# * 文字处理部分
class Handle:
    '''
    用以处理简介、搜索结果输出
    '''

    def __init__(self, raw: str) -> None:
        self.raw: str = raw

    def nn_to_n(self) -> str:
        '''
        将文本中的两个回车替换为一个回车
        '''
        return re.sub(r"\n\n", r"\n", self.raw)

    def refer_to_list(self, max: int = 0) -> list:
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
        return (
            txt
            if len(txt) <= max or not max else
            txt[:max] + f'……\n[字数大于{max}字部分被省略]'
        )


# * 子命令
class Cmd_member:
    """无权限限制命令
    """
    @classmethod
    async def ls(cls, args):
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
    async def select_mwiki(
        cls, wiki_name: str, group_id: int
    ) -> Optional[MWiki]:
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
            for _wiki in wiki_list:
                if wiki_name == _wiki.name:
                    return _wiki
        else:
            # * 不存在对应wiki配置
            return None

    @classmethod
    async def demo(cls, args: dict):
        return json.dumps(args)


class Cmd_admin:
    """管理员权限命令
    """
    @classmethod
    async def add(cls, args):
        """#增加记录

        Args:
            args (dict): 传入参数

        Returns:
            str: 执行结果
        """
        try:
            fn_args = args['fn_args']
            url = (fn_args[1] if fn_args[1][-1] == r'/' else fn_args[1]+r'/')
            if not (url[0:7] == 'https://' or url[0:6] == 'http://'):
                url = 'https://' + url
            mwiki = MWiki(
                name=fn_args[0],
                api_url=((url+'api.php') if len(fn_args) == 2 else fn_args[1]),
                curid_url=(
                    (url+'index.php?curid=')
                    if len(fn_args) <= 2 else
                    fn_args[2]
                ),
                need_proxy=(
                    False
                    if len(fn_args) <= 3 else
                    bool(int(fn_args[3]))
                ),
                user_agent=(
                    r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
                        \(KHTML, like Gecko) Chrome/102.0.5005.63\
                         Safari/537.36'
                    if len(fn_args) <= 4 else
                    ''.join(fn_args[4:])
                )

            )
        except Exception as err:
            return str(err)
        try:
            wiki.set_api_url(mwiki.api_url)
            wiki.set_user_agent(mwiki.user_agent)
            wiki.set_proxies(Config.proxies if mwiki.need_proxy else dict())
            await wiki.search('1')
        except Exception as err:
            return str(err)
        else:
            Data().add_wiki(mwiki, args['group_id'])
            return '记录完成'

    @classmethod
    async def rm(cls, args) -> str:
        Data().remove_wiki(args['fn_args'][0], args['group_id'])

        return "移除wiki成功！"
