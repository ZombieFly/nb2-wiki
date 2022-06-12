import mediawiki as wiki

wiki.set_proxies({'http':'http://127.0.0.1:10809','https':'http://127.0.0.1:10809'})
wiki.set_api_url('https://minecraft.fandom.com/zh/api.php')
wiki.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36')
print(wiki.summary('Java版1.7.2/开发版本', chars=200))
print('\n')
kword = '1.17'
result = wiki.search(kword)
if result[0] == kword:
    try:
        print(wiki.summary(result[0], chars=200))
    except wiki.exceptions.DisambiguationError as msg:
        print(msg)
elif len(result) == 0:
    print('None')
else:
    print(result)