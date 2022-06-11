import mediawiki as wiki

wiki.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36')
print(wiki.API_URL)
print(wiki.summary('猫耳娘'))