"""
此单文件引用了 j1g5awi/nonebot-plugin-mcstatus 的代码，并在此基础上稍加修改，在此对开发者表示感谢
源文件:https://github.com/nonepkg/nonebot-plugin-mcstatus/blob/master/nonebot_plugin_mcstatus/data.py

"""

from pathlib import Path
from typing import Dict, List, Optional, Union, cast

import yaml
from pydantic import BaseModel


class MWiki(BaseModel):
    """MWiki
    """
    name: str = ''
    api_url: str = ''
    curid_url: str = ''
    user_agent: Optional[str] = None
    need_proxy: bool = False


WikiList = Dict[str, Dict[int, List[MWiki]]]


class Data:
    __wiki_list: WikiList = {"user": {}, "group": {}}
    __path: Path

    def __init__(
        self,
        path: Path = Path() / "data" / "mediawiki_search" / "wiki_list.yml"
    ):
        self.__path = path
        self.__load()

    def get_wiki_list(
        self, group_id: Optional[int] = None
    ) -> Union[WikiList, List[MWiki]]:

        wiki_list = self.__wiki_list

        if group_id:
            if group_id not in wiki_list["group"]:
                wiki_list["group"][group_id] = []
            return wiki_list["group"][group_id]
        else:
            return wiki_list

    def add_wiki(
        self,
        wiki: MWiki,

        group_id: Optional[int] = None,
    ):
        wiki_list = cast(List[MWiki], self.get_wiki_list(group_id))
        if wiki not in wiki_list:
            wiki_list.append(wiki)

        self.__wiki_list["group"][group_id] = wiki_list  # type: ignore

        self.__dump()

    def remove_wiki(
        self,
        name: str,
        group_id: Optional[int] = None,
    ):

        wiki_list = list(
            filter(
                lambda wiki: wiki.name != name,
                cast(List[MWiki], self.get_wiki_list(group_id)),
            )
        )

        if wiki_list:
            self.__wiki_list["group"][group_id] = wiki_list  # type: ignore
        else:
            self.__wiki_list["group"].pop(group_id)  # type: ignore

        self.__dump()

    def __load(self):
        try:
            wiki_list = yaml.safe_load(self.__path.open("r", encoding="utf-8"))
            for type in wiki_list:
                for id in wiki_list[type]:
                    self.__wiki_list[type][id] = [
                        MWiki(**wiki) for wiki in wiki_list[type][id]
                    ]
        except FileNotFoundError:
            self.__wiki_list = {"user": {}, "group": {}}

    def __dump(self):
        self.__path.parent.mkdir(parents=True, exist_ok=True)
        wiki_list = {"user": {}, "group": {}}
        for type in self.__wiki_list:
            for id in self.__wiki_list[type]:
                wiki_list[type][id] = [
                    wiki.dict() for wiki in self.__wiki_list[type][id]
                ]
        yaml.dump(
            wiki_list,
            self.__path.open("w", encoding="utf-8"),
            allow_unicode=True,
        )
