"""无权限限制命令
"""


from ..data import Data


async def ls(args: dict) -> str:
    wiki_list = Data().get_wiki_list(args['group_id'])

    if wiki_list:
        result = "本群wiki记录列表如下：\n" + "\n".join(
            f"[{wiki.name}]{wiki.api_url[:-8]}"  # type: ignore
            for wiki in wiki_list
        )
    else:
        result = "本群wiki记录为空"

    return result


async def demo(args: dict) -> str:
    return str(args)
