from ast import expr_context
import re
import mediawiki as wiki
from handle import Handle

wiki.set_proxies({'http://':'http://127.0.0.1:10809','https://':'http://127.0.0.1:10809'})
wiki.set_api_url('https://minecraft.fandom.com/zh/api.php')
wiki.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36')
wiki.set_wiki_url('https://minecraft.fandom.com/zh/wiki')
#print(wiki.summary('Java版1.7.2/开发版本', chars=200))
kword = "1.17"
try:
    result = [kword, Handle(kword).title_to_url(), Handle(wiki.summary(kword)).chars_limit(limit=200)]
    print(result)
except wiki.exceptions.DisambiguationError as msg:
    print(Handle(msg).refer_to_list())
    

'''
if result[0] == kword:
    try:
        contx = wiki.summary(result[0], chars=200)
        print(Handle(contx[1].nn_to_n()))
        print(contx[0])
    except wiki.exceptions.DisambiguationError as msg:
        print(Handle(msg).refer_to_list())
elif len(result) == 0:
    print('None')
else:
    print(result)
'''
