# nb2-wiki

[![OSCS Status](https://www.oscs1024.com/platform/badge/ZombieFly/nb2-wiki.svg?size=small)](https://www.oscs1024.com/project/ZombieFly/nb2-wiki?ref=badge_small)
[![wakatime](https://wakatime.com/badge/user/c7a593a9-08b3-4b3a-96a4-89d3ed7cabd0/project/8595390e-81e5-4c87-93f5-8c598ca49289.svg)](https://wakatime.com/badge/user/c7a593a9-08b3-4b3a-96a4-89d3ed7cabd0/project/8595390e-81e5-4c87-93f5-8c598ca49289)

基于[wikipedia](https://github.com/goldsmith/Wikipedia)，适用于 [Nonebot2](https://github.com/nonebot/nonebot2) 的 mediawiki搜索 插件，同时你的Nonebot版本应不低于Nonebot2.0b1。 

## 关于
本项目作为[AXbot/mws.py](https://github.com/ZombieFly/AXbot/blob/master/mws.py)的重构nonebot2适配版，代码逻辑已然完全不同，并且功能得到了更大的拓展，但仍旨在能于即时通讯平台中快速引用wiki条目，让由各大wiki中所整合的知识为更多人所用。

该项目目前仍属于较高频率代码变更状态，未发布正式版，可能并不合适立即投入生产环境，请务必于测试环境中进行调试后再投入生产环境。

## 安装
克隆此仓库至nonebot生成的目录中对应的存放插件的文件夹内。
```bash
git clone https://github.com/ZombieFly/nb2-wiki.git
```

## 配置
可配置项存放于``config.py``内，可按需求更改 ~~，或是直接于``__init__.py``内声明全局变量~~（现仅从nb获得配置）
- ``PROXIES``(dict)：代理地址，默认值为``{}``，当所使用的MWiki的``need_proxy``为``True``时使用；

- ``REFER_MAX``(int)：相关搜索结果最大返回值，默认值为``10``；

- ``RETRY_TIMES``(int)：api返回错误时最大重试次数，默认值为``1``；

- ``RAW_MWIKI``(MWiki): 默认MWiki对象，在直接使用``/wiki <关键词>``命令时会使用此wiki记录；

- ``CMD_START``(list)：命令触发头，默认值为``['wiki', '维基']``。

## 使用
以下命令实例中，假定bot配置的命令头为``.``、``/``，请依据实际情况替换。

- ##### ``/wiki <关键词>`` <br>
通过``raw_MWiki``发起搜索，一个可用实例：
```
/wiki 绵羊
```

- ##### ``/wiki.add <自定义wiki简称> <wiki地址> <-d/D （可选）>``<br>
    - 其中，``wiki地址``应为``/api.php``或``/index.php?curid=``前部分，链接开头的http协议可省略，（如``minecraft.fandom.com/zh/``）。当需要使用的api与curid链接前部分不相同时，可在记录后，使用``set``子命令进行修改;
    - 此外，命令中两处的``/``、``.``可替换为**任一被定义的命令头**，例如在本文档假设的环境中，``.wiki/add``、``/wiki/add``等的皆可触发此子命令，下文将不再赘述此特征；
    - 末尾可选参数 ``-D`` 或 ``-d``，添加后，将跳过wiki api可用性检查，直接记录wiki。
    - 一个可用的实例：
        ```
        .wiki.add mc minecraft.fandom.com/zh/ -D
        ```

- ##### ``.wiki.set <已记录wiki名> <属性> <值>``
  修改已记录的wiki的对应属性，``属性``应该为 ``name``、``api_url``、``curid_url`` 等的MWiki属性，``<值>``为所需要更改后的值。

- ##### ``.wiki.rm <已记录wiki名>``
  从本群记录中移除指定已记录wiki。

- ##### ``.wiki.<已记录wiki名> <关键词>``
  指定使用一个已记录的wiki发起搜索。一个可能的实例:
  ```
  .wiki.moe 别当欧尼酱了
  ```

- ##### ``.wiki.ls``
  列出本群所有已记录wiki。

- ##### ``.wiki.lsl <已记录wiki名>``
  以json形式返回目标已记录wiki的完全记录内容，当不追加参数指定wiki时将返回配置文件中的`RAW_MWIKI`。


## 待办
- [x] add子命令判断wiki api是否可用，以及是否可直接生成简介
- [x] 默认UA储存问题
- [x] bilibili wiki适配器
- [x] add子命令添加的wiki名称已被使用，阻止注册
- [x] rm子命令删除时无论是否存在目标wiki都是返回“删除成功”，应当增加wiki存在性判定
- [ ] 优化搜索流程，减少请求数，亦或是提高网络I/O利用率
- [ ] 优化api检查机制
