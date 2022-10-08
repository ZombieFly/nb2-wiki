<div align="center">

# nonebot-plugin-wiki

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/ZombieFly/nb2-wiki.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-example">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-wiki.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
<a href="https://wakatime.com/badge/github/ZombieFly/nb2-wiki"><img src="https://wakatime.com/badge/github/ZombieFly/nb2-wiki.svg" alt="wakatime"></a>

</div>


基于 [wikipedia](https://github.com/goldsmith/Wikipedia)，适用于 [Nonebot2](https://github.com/nonebot/nonebot2) 的 mediawiki搜索 插件，同时你的Nonebot版本应不低于Nonebot2.0b1。 

## 关于
- 本项目作为 [AXbot/mws.py](https://github.com/ZombieFly/AXbot/blob/master/mws.py) 的重构 nonebot2 适配版，代码逻辑已然完全不同，并且功能得到了更大的拓展，但仍旨在能于即时通讯平台中快速引用wiki条目，让由各大wiki中所整合的知识为更多人所用。

- 不止步于mediawiki api，本项目正在尝试兼容Bilibili wiki。依托于 [XZhouQD/nonebot-plugin-bwiki-navigator](https://github.com/XZhouQD/nonebot-plugin-bwiki-navigator.git) ，已具备部分兼容性，同时，[基于网页解析](https://github.com/ZombieFly/nb2-wiki/commit/f85f93a49dacbe99fa4025acc93f6f13326bfcb3)的简介获取正在优化。 

- 该项目目前仍未发布正式版，可能并不适合立即投入生产环境，请务必于测试环境中进行调试后再投入生产环境。

## 安装

### 通过 nb-cli 安装（推荐）
```bash
nb plugin install nonebot-plugin-wiki
```

### 通过 pip 安装
```bash
pip install nonebot_plugin_wiki
```

### 从 github 仓库克隆
克隆此仓库至 nonebot 生成的目录中对应的存放插件的文件夹内。
```bash
git clone https://github.com/ZombieFly/nb2-wiki.git
```

## 配置
本插件默认使用 中文 Minecraft Wiki 作为 ``RAW_MWIKI`` 记录，如需更改 ，可依照 nonebot 的 [配置方法](https://v2.nonebot.dev/docs/tutorial/configuration) 对插件进行定制，以下配置项为可选配置：
- ``PROXIES``：代理地址，默认值为 ``{}``，当所使用的MWiki的 ``need_proxy``为``True``时使用；

- ``REFER_MAX``：相关搜索结果最大返回值，默认值为 ``10``；

- ``RETRY_TIMES``：api返回错误时最大重试次数，默认值为 ``1``；

- ``RAW_MWIKI``: 默认MWiki对象，在直接使用``/wiki <关键词>``命令时会使用此wiki记录，默认值为 ``{"name": "mc","api_url": "https://minecraft.fandom.com/zh/api.php","curid_url": "https://minecraft.fandom.com/zh/index.php?curid=","user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit 537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36","need_proxy": false}``；

- ``CMD_START``：命令触发头，默认值为``["wiki", "维基"]``。

## 使用
以下命令实例中，假定bot配置的命令头为 ``.``、``/``，请依据实际情况替换。

- ##### ``/wiki <关键词>`` <br>
  通过 ``raw_MWiki`` 发起搜索，一个可用实例：
  ```
  /wiki 绵羊
  ```

- ##### ``/wiki.add <自定义wiki简称> <wiki地址> <-d/D （可选）>``（限群管理员权限）<br>
  - 其中，``wiki地址`` 应为 ``/api.php`` 或 ``/index.php?curid=`` 前部分，链接开头的http协议可省略，（如 ``minecraft.fandom.com/zh/`` ）。当需要使用的api与curid链接前部分不相同时，可在记录后，使用``set``子命令进行修改;
   - 此外，命令中两处的 ``/`` 、 ``.`` 可替换为**任一被定义的命令头**，例如在本文档假设的环境中， ``.wiki/add`` 、 ``/wiki/add`` 等的皆可触发此子命令，下文将不再赘述此特征；
  - 末尾可选参数 ``-D`` 或 ``-d``，添加后，将跳过wiki api可用性检查，直接记录wiki。
  - 一个可用的实例：
    ```
    .wiki.add mc minecraft.fandom.com/zh/ -D
    ```

- ##### ``.wiki.set <已记录wiki名> <属性> <值>`` （限群管理员权限）
  修改已记录的wiki的对应属性，``属性``应该为 ``name``、``api_url``、``curid_url`` 等的MWiki属性， ``值`` 为所需要更改后的值。

- ##### ``.wiki.rm <已记录wiki名>``（限群管理员权限）
  从本群记录中移除指定已记录wiki。

- ##### ``.wiki.<已记录wiki名> <关键词>``
  指定使用一个已记录的wiki发起搜索。一个可能的实例:
  ```
  .wiki.moe 别当欧尼酱了
  ```

- ##### ``.wiki.ls``
  列出本群所有已记录wiki。

- ##### ``.wiki.lsl <已记录wiki名>``（限群管理员权限）
  以json形式返回目标已记录wiki的完全记录内容，当不追加参数指定wiki时将返回配置文件中的 `RAW_MWIKI`。


## 待办
- [x] add子命令判断wiki api是否可用，以及是否可直接生成简介
- [x] 默认UA储存问题
- [x] bilibili minecraft wiki适配器
- [x] add子命令添加的wiki名称已被使用，阻止注册
- [x] rm子命令删除时无论是否存在目标wiki都是返回“删除成功”，应当增加wiki存在性判定
- [ ] 优化Biliwiki mc镜像简介生成结果
- [ ] 兼容更多的Bilibili Wiki
- [x] 搜索时返回内容不是合规的json时的异常处理
- [ ] 优化搜索流程，减少请求数，亦或是提高网络I/O利用率
- [ ] 优化api检查机制
- [ ] 搜索结果缓存
