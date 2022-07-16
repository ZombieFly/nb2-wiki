from pydantic import BaseSettings


class Config(BaseSettings):
    # 代理地址。如果完全不会使用代理地址可忽略此配置
    PROXIES:dict = {'All://':'http://127.0.0.1:10809'}
    # 相关结果最大返回数
    REFER_MAX:int = 10
    class Config:
        extra = "ignore"