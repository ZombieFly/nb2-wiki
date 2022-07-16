# nb2-wiki

[![OSCS Status](https://www.oscs1024.com/platform/badge/ZombieFly/nb2-wiki.svg?size=small)](https://www.oscs1024.com/project/ZombieFly/nb2-wiki?ref=badge_small)
[![wakatime](https://wakatime.com/badge/user/c7a593a9-08b3-4b3a-96a4-89d3ed7cabd0/project/8595390e-81e5-4c87-93f5-8c598ca49289.svg)](https://wakatime.com/badge/user/c7a593a9-08b3-4b3a-96a4-89d3ed7cabd0/project/8595390e-81e5-4c87-93f5-8c598ca49289)

基于[wikipedia](https://github.com/goldsmith/Wikipedia)，适用于 [Nonebot2](https://github.com/nonebot/nonebot2) 的 mediawiki搜索 插件，同时你的Nonebot版本应不低于Nonebot2.0b1。 

## 关于
本项目作为[AXbot/mws.py](https://github.com/ZombieFly/AXbot/blob/master/mws.py)的重构nonebot2适配版，代码逻辑已然完全不同，并且功能得到了更大的拓展，但仍旨在能于即时通讯平台中快速引用wiki条目，让由各大wiki中所整合的知识为更多人所用。

## 安装
克隆此仓库至nonebot生成的目录中对应的存放差插件的文件夹内。
```shell
git clone https://github.com/ZombieFly/nb2-wiki.git
```

## 配置
- ``PROXIES``(dict)：代理地址，默认值为``{'All://':'http://127.0.0.1:10809'}``，当所使用的MWiki的``need_proxy``为``True``时使用，可在``config.py``中声明，亦可于``__init__.py``中声明全局变量；

- ``REFER_MAX``(int)：相关搜索结果最大返回值，默认值为``10``，配置方式同``PROXIES``；

- ``raw_MWiki``(MWiki): 默认MWiki对象，在直接使用``/wiki <关键词>``时会使用此wiki记录。

## 使用
以下命令实例中，假定bot配置的命令头为``.``、``/``，请依据实际情况替换

- ##### ``/wiki <关键词>`` <br>
通过``raw_MWiki``发起搜索，一个可用实例：``/wiki 绵羊``

- ##### ``/wiki.add <自定义wiki简称> <wiki地址>``<br>
    - 其中，``wiki地址``应为``/api.php``或``/index.php?curid=``前部分，链接开头的http协议可省略，（如``minecraft.fandom.com/zh/``）。当需要使用的api与curid链接前部分不相同时，应采用下文的可选形式分开指定;
    - 此外，命令中两处的``/``、``.``可替换为**任一被定义的命令头**，例如在本文档假设的环境中，``.wiki/add``、``/wiki/add``等的皆可触发此子命令，下文将不再反复提及此特征。
    - 一个可用的实例：``.wiki.add mc minecraft.fandom.com/zh/``
    - 除``<自定义wiki简称>``与``<api地址>``两个必选参数外，此子命令仍包含多种可选形式：
      - ##### ``.wiki.add <自定义wiki简称> <api地址> <curid地址>``<br>
        ``api地址``应形如``https://minecraft.fandom.com/zh/api.php``，``<curid地址>``应形如``http://minecraft.fandom.com/zh/index.php?curid=``，请于上文中的最简命令相区分，此处的两地址必须为完整地址，包括http协议也不可省略。一个可用的实例：``.wiki.add moe https://mobile.moegirl.org.cn/api.php https://zh.moegirl.org.cn/index?curid=``；
      - ##### ``.wiki.add <自定义wiki简称> <api地址> <curid地址> <是否使用代理>``<br>
        相较上一形式，此形式于增加``<是否使用代理>``参数，可选值为``1``或``0``，分别决定是否使用由``PROXIES``指定的代理地址
      
      - ##### ``.wiki.add <自定义wiki简称> <api地址> <curid地址> <是否使用代理> <UA>``<br>
        相较上一形式，此形式于增加``<UA>``参数，即指定发起请求时使用的UA，内可含空格。一个可用的实例：``.wiki.add moe https://mobile.moegirl.org.cn/api.php https://zh.moegirl.org.cn/index?curid= Mozilla/5.0(Linux;Android12;SM-F9160Build/SP1A.210812.016;wv)AppleWebKit/537.36(KHTML,likeGecko)Version/4.0Chrome/102.0.5005.78MobileSafari/537.36``

- ##### ``.wiki.rm <自定义wiki简称>``
  从本群记录中移除指定已记录wiki

- ##### ``.wiki.list``
  列出本群所有已记录wiki
  