"""无权限限制命令
"""


from ..data import Data


async def ls(args: dict) -> str:
    return ("本群wiki记录列表如下：\n"
            + "\n".join(f"[{wiki.name}]{wiki.api_url[:-8]}"   # type: ignore
                        for wiki in wiki_list)
            ) if (wiki_list := Data().get_wiki_list(args['group_id'])) else "本群wiki记录为空"


async def demo(args: dict) -> str:
    return str(args)
