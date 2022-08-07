"""管理员权限命令
"""

from json import dumps
import traceback
from typing import cast

from .utils import Status, args2mwiki, check_wiki
from ..data import Data, MWiki
from . import admin, member


async def lsl(args: dict):
    if len(args['fn_args']):
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

    else:
        return dumps(args['config'].RAW_MWIKI)


async def add(args: dict) -> str:
    """#增加记录

    Args:
        args (dict): 传入参数

    Returns:
        str: 执行结果
    """
    # * 阻止注册类属性作为名称
    if args['fn_args'][0] in dir(admin) + dir(member):
        return f'不被允许注册保留关键字<{args["fn_args"][0]}>作为名称'
    # * 阻止使用已注册的名称
    if Data().has_wiki(args['fn_args'][0], args['group_id']):
        return '该名称已被注册'
    try:

        # 构造Mwiki对象用以记录
        if len(args['fn_args']) in (0, 1):
            raise IndexError
        mwiki = args2mwiki(
            args=args['fn_args'], raw_mwiki=args['config'].RAW_MWIKI)
    except IndexError:
        return '参数缺省，请重新输入'
    except Exception:
        return traceback.format_exc()

    if args['fn_args'][-1] not in ('-d', '-D'):
        # 未追加 -D/-d 时，检查api可用性
        try:
            # * 判断wiki api可用性
            api_status = await check_wiki(mwiki, args['config'].PROXIES)
            if api_status != Status.OK:
                return api_status.get_msg()

        except Exception:
            return traceback.format_exc()

    Data().add_wiki(mwiki, args['group_id'])
    return '记录完成'


async def set(args: dict) -> str:
    return ''


async def rm(args: dict) -> str:
    try:
        if Data().remove_wiki(args['fn_args'][0], args['group_id']):
            return "移除wiki成功！"
        else:
            return "不存在这个名称的已记录wiki"
    except Exception:
        return traceback.format_exc()
