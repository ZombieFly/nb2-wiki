import re
import json
from typing import Dict, Optional
import traceback

from .data import Data, MWiki

from . import mediawiki as Wiki

from .config import Config


def url_format(url: str) -> str:
    """给url加上https协议头与/后缀（如果没有的话）
    """
    url = (url if url[-1] == r'/' else url + r'/')
    if not (url[0:7] == 'https://' or url[0:6] == 'http://'):
        url = 'https://' + url
    return url


def set_wiki(mwiki: MWiki, proxies: Dict = dict()):
    Wiki.set_api_url(mwiki.api_url)
    Wiki.set_curid_url(mwiki.curid_url)
    Wiki.set_user_agent(mwiki.user_agent)
    Wiki.set_proxies(proxies if mwiki.need_proxy else dict())
    return None


# * 文字处理部分
class Handle:
    '''
    用以处理简介、搜索结果输出
    '''
    @classmethod
    def nn_to_n(cls, raw) -> str:
        '''
        将文本中的两个回车替换为一个回车
        '''
        return re.sub(r"\n\n", r"\n", raw)

    @classmethod
    def refer_to_list(cls, raw: str, max: int = 0) -> list:
        '''
        将建议列表以列表形式输出,参数max控制返回列表最大长度
        '''
        ret: list = raw.options  # type: ignore
        return ret if (max >= len(ret) or not max) else ret[:max]

    @classmethod
    def chars_max(cls, raw: str, txt='', max=0) -> str:
        '''
        控制输入文本最大字数,并在末尾追加省略信息
        '''
        txt = (raw if not txt else txt)
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
    async def check_wiki(cls, mwiki: MWiki):
        pass

    @classmethod
    async def ls(cls, args):
        wiki_list = Data().get_wiki_list(args['group_id'])

        if wiki_list:
            result = "本群wiki记录列表如下：\n" + "\n".join(
                f"[{wiki.name}]{wiki.api_url[:-8]}"  # type: ignore
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
            wiki.name  # type: ignore
            for wiki in wiki_list
        ):
            for _wiki in wiki_list:
                if wiki_name == _wiki.name:  # type: ignore
                    return _wiki  # type: ignore
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
        # * 阻止注册类属性作为名称
        if args['fn_args'][0] in (dir(cls) and dir(Cmd_member)):
            return f'不被允许注册保留关键字<{args["fn_args"][0]}>作为名称'
        try:
            fn_args = args['fn_args']
            # 对url进行处理
            url = url_format(fn_args[1])
            # 构造Mwiki对象用以记录
            mwiki = MWiki(
                name=fn_args[0],
                api_url=((url + 'api.php') if len(fn_args) == 2 else url),
                curid_url=(
                    (url + 'index.php?curid=')
                    if len(fn_args) <= 2 else
                    url_format(fn_args[2])
                ),
                need_proxy=(
                    False
                    if len(fn_args) <= 3 else
                    bool(int(fn_args[3]))
                ),
                user_agent=(
                    (
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
                        r'AppleWebKit/537.36\(KHTML, like Gecko) Chrome/' +
                        '102.0.5005.63 Safari/537.36'
                    )
                    if len(fn_args) <= 4 else
                    ''.join(fn_args[4:])
                )

            )
        except Exception:
            return traceback.format_exc()

        try:
            # * 判断wiki api可用性
            set_wiki(mwiki, Config.__annotations__['PROXIES'])
            query = await Wiki.random()
            await Wiki.search(query[0])
        except Exception:
            return traceback.format_exc()
        else:
            Data().add_wiki(mwiki, args['group_id'])
            return '记录完成'

    @ classmethod
    async def rm(cls, args) -> str:
        Data().remove_wiki(args['fn_args'][0], args['group_id'])

        return "移除wiki成功！"
