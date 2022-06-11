import mediawiki as wiki

wiki.set_api_url('https://minecraft.fandom.com/zh/api.php')
wiki.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36')
print(wiki.summary('Java版1.7.2/开发版本', chars=150))