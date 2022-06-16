import mediawiki as wiki
from handle import Handle


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
