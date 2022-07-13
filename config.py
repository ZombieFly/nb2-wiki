from pydantic import BaseSettings


class Config(BaseSettings):
    # Your Config Here
    proxies = {'All://':'http://127.0.0.1:10809'}
    class Config:
        extra = "ignore"