from nonebot import get_driver, on_command
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from .config import Config

from . import mediawiki as wiki
from .handle import Handle

global_config = get_driver().config
config = Config.parse_obj(global_config)

wiki.set_proxies({'http://':'http://127.0.0.1:10809','https://':'http://127.0.0.1:10809'})
wiki.set_api_url('https://minecraft.fandom.com/zh/api.php')
wiki.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36')
wiki.set_wiki_url('https://minecraft.fandom.com/zh/wiki')

refer_max = 10
head = '搜索结果出来了喵:'

cmd = on_command('wiki ')

# TODO
# ! 目前重定向可能会出现完全不相干的结果返回，同时，因为发送的链接是直接把title转码得到的，所以有时候也没法访问到被重新向的链接
def output(title, auto_suggest= True, redirect= True):
    result = [title, Handle(title).title_to_url(), Handle(wiki.summary(title, auto_suggest= auto_suggest, redirect= redirect)).chars_limit(limit=200)]
    return (f'{head}\n'
            +f'{result[1]}\n'
            +f'{result[2]}')

@cmd.handle()
async def _(event: GroupMessageEvent, state: T_State, keywd= CommandArg()):
    #await cmd.send(str(state))
    numb:str = event.message.extract_plain_text()
    if numb and not keywd:
        try:
            numb = int(numb)
            await cmd.finish(output(state['results'][numb], False, False))
        except ValueError:
            #输入的非数字时的处理
            await cmd.finish('取消搜索')
        except IndexError:
            #给的数大了
            await cmd.finish(f'{numb}超出了索引')

    else:
        #会话开启的第一次处理
        #await cmd.send(f'keywd={keywd.extract_plain_text()}, type(keywd)={type(keywd.extract_plain_text())}')
        try:
            #有直接对应的页面
            await cmd.finish(output(keywd.extract_plain_text(), redirect= False))
        except wiki.exceptions.DisambiguationError as msg:
            #没有对应页面，但可生成相似结果列表
            state['results'] = Handle(msg).refer_to_list(max=refer_max)
            await cmd.reject('有关结果如下，输入对应标号发起搜索，回复其他字符自动取消:\n' + 
                            '\n'.join(f'[{n}]{state["results"][n]}'
                            for n in range(len(state['results']))) +
                            f'\n(仅展示前{refer_max}个结果)'
                            )
        except wiki.exceptions.PageError:
            await cmd.finish('没有找到任何相关结果')
        