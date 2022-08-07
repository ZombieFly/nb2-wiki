"""管理员权限命令
"""

from json import dumps
import traceback
from typing import cast

from .utils import Status, args2mwiki, check_wiki, get_mwiki
from ..data import Data, MWiki
from . import admin, member


async def lsl(args: dict):
    if len(args['fn_args']):
        mwiki = get_mwiki(
            wiki_name=args['fn_args'][0], group_id=args['group_id'])
        if type(mwiki) is str:
            return mwiki
        else:
            return dumps(cast(MWiki, mwiki).dict())

    else:
        return dumps(args['config'].RAW_MWIKI.dict())


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
    # * 阻止参数缺省
    if len(args['fn_args']) in (0, 1):
        return '参数缺省，请重新输入'

    try:

        # 构造Mwiki对象用以记录
        mwiki = args2mwiki(
            args=args['fn_args'], raw_mwiki=args['config'].RAW_MWIKI)
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

    if len(args['fn_args']) == 3:

        wiki_name = args['fn_args'][0]
        _key = args['fn_args'][1]
        _value = args['fn_args'][2]
        _group_id = args['group_id']

        mwiki = get_mwiki(
            wiki_name=wiki_name, group_id=_group_id)

        if type(mwiki) is str:
            ret = mwiki

        else:
            if _key in cast(MWiki, mwiki).dict().keys():

                # 删除原始记录
                await rm(args)
                # 修改参数
                setattr(mwiki, _key, _value)
                # 写入
                Data().add_wiki(cast(MWiki, mwiki), _group_id)
                # 返回json格式的修改后的wiki记录
                if _key == 'name':
                    # 更改wiki记录名时一同修改缓存内wiki名
                    args['fn_args'][0] = _value

                ret = await lsl(args)
                ret = f'修改后的wiki记录为：\n{ret}'

            else:
                ret = '目标wiki不存在此属性'
    else:
        ret = '参数项数错误，请依照格式重新输入'

    return ret


async def rm(args: dict) -> str:
    try:
        if Data().remove_wiki(args['fn_args'][0], args['group_id']):
            return "移除wiki成功！"
        else:
            return "不存在这个名称的已记录wiki"
    except Exception:
        return traceback.format_exc()
