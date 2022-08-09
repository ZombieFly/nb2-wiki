from typing import Dict, Union
from pydantic import BaseModel, Extra

from .data import MWiki


class Config(BaseModel, extra=Extra.ignore):
    # 代理地址。如果完全不会使用代理地址可忽略此配置
    proxies: dict = {}
    # 最大重试请求数目（api返回错误时）
    retry_times: int = 1
    # 相关结果最大返回数
    refer_max: int = 10
    # 默认MWiki
    raw_mwiki: Union[Dict, MWiki] = {
        'name': 'mc',
        'api_url': 'https://minecraft.fandom.com/zh/api.php',
        'curid_url': 'https://minecraft.fandom.com/zh/index.php?curid=',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit 537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
        'need_proxy': False
    }
    # 可用触发命令头
    cmd_start: list = ['wiki', '维基']
