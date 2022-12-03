from enum import unique, Enum
from json.decoder import JSONDecodeError
from typing import Optional, Union, cast, Dict

from httpx import ConnectError

from ..mediawiki.exceptions import ApiReturnError, NoExtractError

from .. import mediawiki as Wiki
from ..data import Data, MWiki


@unique
class Status(Enum):
    OK = {"200": "可生成简介"}
    SUMMARY_ERROR = {"204": "api可用，不可生成简介"}
    API_ERROR = {"400": "api不可用"}
    API_RETURN_ERROR = {"002": "重试预设次数后，api依然返回错误，请检查api能否正常工作"}
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
        url = url if url[-1] == '/' else f'{url}/'
    if url[:8] != 'https://' and url[:7] != 'http://':
        url = f'https://{url}'
    return url


def set_wiki(mwiki: MWiki, proxies: Dict[str, str] = dict()):
    Wiki.set_api_url(mwiki.api_url)
    Wiki.set_curid_url(mwiki.curid_url)
    Wiki.set_user_agent(mwiki.user_agent)
    Wiki.set_proxies(proxies if mwiki.need_proxy else dict())
    return None


def args2mwiki(args: dict, raw_mwiki: MWiki) -> MWiki:
    """将以列表形式传入的参数，解析为MWiki对象返回

    Args:
        args (list): 参数
        raw_mwiki (MWIKI): 默认MWiki（缺省填充）

    Returns:
        MWiki: MWiki对象
    """
    target = cast(MWiki, raw_mwiki)
    _it = iter(args)

    target.name = next(_it)
    target.api_url = url_format(next(_it))

    target.curid_url = f'{target.api_url}index.php?curid='

    target.api_url = f'{target.api_url}api.php'

    return target


async def check_wiki(mwiki: MWiki, proxies: Dict[str, str] = dict()) -> Status:
    """检查wiki api可用性

    Args:
        mwiki (MWiki): 待检测MWiki对象
        proxies (Dict[str, str], optional): 代理设置. Defaults to dict().

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
    except ApiReturnError:
        return Status.API_RETURN_ERROR
    except Exception as err:
        raise err
    else:
        return Status.OK


async def select_mwiki(wiki_name: str, group_id: int) -> Optional[MWiki]:
    # sourcery skip: remove-unnecessary-else, swap-if-else-branches
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


def get_mwiki(wiki_name: str, group_id: int) -> Union[MWiki, str]:

    if Data().has_wiki(wiki_name, group_id):
        wiki_list = Data().get_wiki_list(group_id)
        for twiki in wiki_list:

            if cast(MWiki, twiki).name == wiki_name:
                return cast(MWiki, twiki)

    return '不存在对应的已记录wiki'
