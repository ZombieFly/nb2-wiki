import re
from json import dumps
from json.decoder import JSONDecodeError
from enum import Enum, unique
from typing import Dict, Optional, cast
import traceback

from httpx import ConnectError

from .data import Data, MWiki

from . import mediawiki as Wiki
from .mediawiki.exceptions import NoExtractError


@unique
class Status(Enum):
    OK = {"200": "可生成简介"}
    SUMMARY_ERROR = {"204": "api可用，不可生成简介"}
    API_ERROR = {"400": "api不可用"}
    DOMAIN_ERROR = {"000": "域名解析异常，请检查输入是否正确"}
    URL_ERROR = {"403": "链接不可达，请检查输入"}
    PROXY_ERROR = {"001": "代理格式有误"}

    def get_code(self) -> str:
        """获取状态码

        Returns:
            int: 状态码
        """
        return list(self.value.keys())[0]

    def get_msg(self) -> str:
        """获取状态信息

        Returns:
            str: 状态信息
        """
        return list(self.value.values())[0]


def url_format(url: str, need_slash=True) -> str:
    """给url加上https协议头与末尾斜杠（可选）

    Args:
        url (str): 原始url
        need_slash (bool, optional): 是否需要在结尾添加斜杠 Defaults to True.

    Returns:
        str: 处理后的url
    """
    if need_slash:
        url = (url if url[-1] == r'/' else url + r'/')
    if not (url[0:8] == 'https://' or url[0:7] == 'http://'):
        url = 'https://' + url
    return url


def set_wiki(mwiki: MWiki, proxies: Dict = dict()):
    Wiki.set_api_url(mwiki.api_url)
    Wiki.set_curid_url(mwiki.curid_url)
    Wiki.set_user_agent(mwiki.user_agent)
    Wiki.set_proxies(proxies if mwiki.need_proxy else dict())
    return None


def args2mwiki(args: dict, raw_mwiki: MWiki) -> MWiki:
    """将以列表形式传入的参数，解析为MWiki对象返回

    Args:
        args (list): 被切分的原始参数

    Returns:
        MWiki: MWiki对象
    """
    target = cast(MWiki, raw_mwiki)
    _it = iter(args)

    try:
        target.name = next(_it)
        target.api_url = url_format(next(_it), need_slash=False)

        np_arg = str()

        try:
            target.curid_url = url_format(next(_it), need_slash=False)
        except StopIteration:
            url = url_format(target.api_url)
            target.api_url = url + 'api.php'
            target.curid_url = url + 'index.php?curid='
            raise StopIteration
        try:
            np_arg = next(_it)
            target.need_proxy = bool(int(np_arg))
        except ValueError:
            raise ValueError(f'指定是否使用代理的参数"{np_arg}"有误，正确的值应该为“0”与“1”中的一个')
        target.user_agent = " ".join(list(_it))

    except StopIteration:
        pass
    except Exception as err:
        raise err

    return target


async def check_wiki(mwiki: MWiki, proxies=dict()) -> Status:
    """检查wiki api可用性

    Args:
        mwiki (MWiki): 待检测MWiki对象
        proxies (dict, optional): 代理设置. Defaults to dict().

    Returns:
        Status
    """
    set_wiki(mwiki, proxies)
    try:
        title = await Wiki.random()
        await Wiki.summary(title)
    except NoExtractError:
        return Status.SUMMARY_ERROR
    except JSONDecodeError:
        return Status.API_ERROR
    except ConnectError:
        return Status.DOMAIN_ERROR
    except AttributeError:
        return Status.PROXY_ERROR
    except Exception as err:
        raise err
    else:
        return Status.OK


async def select_mwiki(wiki_name: str, group_id: int) -> Optional[MWiki]:
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


# * 文字处理部分
class Handle:
    '''
    用以处理简介、搜索结果输出
    '''
    @classmethod
    def nn_to_n(cls, raw: str) -> str:
        '''
        将文本中的两个回车替换为一个回车
        '''
        return re.sub(r"\n\n", r"\n", raw)

    @classmethod
    def refer_to_list(cls, raw: Wiki.exceptions.DisambiguationError, max: int = 0) -> list:
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
    async def ls(cls, args: dict) -> str:
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
    async def demo(cls, args: dict) -> str:
        return dumps(args)


class Cmd_admin:
    """管理员权限命令
    """
    @classmethod
    async def lsl(cls, args: dict):
        name = args['fn_args'][0]
        if Data().has_wiki(name, args['group_id']):
            wiki_list = Data().get_wiki_list(args['group_id'])
            tar_wiki = MWiki()
            for twiki in wiki_list:
                if cast(MWiki, twiki).name == name:
                    tar_wiki = cast(MWiki, twiki)
                    break

            return dumps(tar_wiki.dict())
        else:
            return "不存在目标wiki"

    @classmethod
    async def add(cls, args: dict) -> str:
        """#增加记录

        Args:
            args (dict): 传入参数

        Returns:
            str: 执行结果
        """
        # * 阻止注册类属性作为名称
        if args['fn_args'][0] in (dir(cls) and dir(Cmd_member)):
            return f'不被允许注册保留关键字<{args["fn_args"][0]}>作为名称'
        # * 阻止使用已注册的名称
        if Data().has_wiki(args['fn_args'][0], args['group_id']):
            return '该名称已被注册'
        try:

            # 构造Mwiki对象用以记录
            if len(args['fn_args']) in [0, 1]:
                raise IndexError
            mwiki = args2mwiki(
                args=args['fn_args'], raw_mwiki=args['config'].RAW_MWIKI)
        except IndexError:
            return '参数缺省，请重新输入'
        except Exception:
            return traceback.format_exc()

        try:
            # * 判断wiki api可用性
            api_status = await check_wiki(mwiki, args['config'].PROXIES)
            if api_status == Status.OK:
                Data().add_wiki(mwiki, args['group_id'])
                return '记录完成'
            else:
                return api_status.get_msg()

        except Exception:
            return traceback.format_exc()

    @ classmethod
    async def rm(cls, args: dict) -> str:
        try:
            if Data().remove_wiki(args['fn_args'][0], args['group_id']):
                return "移除wiki成功！"
            else:
                return "不存在这个名称的已记录wiki"
        except Exception:
            return traceback.format_exc()
