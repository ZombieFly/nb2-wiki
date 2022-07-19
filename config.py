from pydantic import BaseSettings
from .data import MWiki

class Config(BaseSettings):
    # 代理地址。如果完全不会使用代理地址可忽略此配置
    PROXIES:dict = {'All://':'http://127.0.0.1:10809'}
    # 相关结果最大返回数
    REFER_MAX:int = 10
    #默认MWiki
    RAW_MWIKI:MWiki = MWiki(name= 'mc',
                            api_url= 'https://minecraft.fandom.com/zh/api.php',
                            curid_url= 'https://minecraft.fandom.com/zh/index.php?curid=',
                            user_agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
                            need_proxy= False
                        )
    #可用触发命令头
    CMD_START:list = ['wiki', '维基']
    
    class Config:
        extra = "ignore"