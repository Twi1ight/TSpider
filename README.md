# TSpider

简单来讲，这货是一个动态web爬虫

## 简介

基于CasperJS和PhantomJS，可以自动渲染网页、动态解析js，支持ajax和各类前端交互。

代码基于[phantomjs爬虫小记](http://blog.wils0n.cn/?post=18) by [wils0n](http://blog.wils0n.cn) ，在tuicool上也有这篇文章[http://www.tuicool.com/articles/JbEfIvV](http://www.tuicool.com/articles/JbEfIvV) ， 原作者的代码在Github上也有[crawler_phantomjs](https://github.com/wilson9x1/crawler_phantomjs)

后来看到[浅谈动态爬虫与去重](http://blog.fr1day.me/2017/01/10/crawler_and_filter/)这篇文章，受益匪浅，其关于url去重部分考虑的非常仔细，我原本只是简单的将纯数字去重。基于其内容，我添加了自定义事件的触发功能。但是文章中说PhantomJS不支持MutationObserver是错误的，实际上从PhantomJS 2.0开始就已经添加了对MutationObserver的支持。

可以用下面这段代码测试：

```javascript
var page = require('webpage').create();
page.onConsoleMessage = function (msg) {
    console.log('MutationObserver Support: ' + msg);
};
page.evaluate(function () {
    var MutationObserver = window.MutationObserver ||
        window.WebKitMutationObserver ||
        window.MozMutationObserver;
    var mutationObserverSupport = !!MutationObserver;
    console.log(mutationObserverSupport);
});
phantom.exit();
```

```bash
Twi1ight at Mac-Pro in ~/Code/TSpider (master)
$ phantomjs support.js
MutationObserver Support: true
```

所以DOMNodeInserted的事件绑定用MutationObserver重写了

我在两者的基础上，增强了交互功能，修复了一些问题，也新增了一些功能。

#### 目前功能：

- 自动填充和提交表单
- 从文件载入cookie
- 过滤广告和统计链接
- 过滤静态资源访问
- 载入cookie后防注销和登出
- 支持各种on*交互事件
- 支持同源iframe页面爬取

#### 依赖：

- casperjs

- phantomjs

- redis

- mongodb

- python 2.7.x

  python modules:

  - publicsuffix
  - pymongo
  - redis

## 设置

大部分设置在settings.py中

```python
class RedisConf(object):
    host = '127.0.0.1'
    port = 6379
    password = None

    db = 0
    # list
    saved = 'spider:url:saved'
    tasks = 'spider:url:task'
    result = 'spider:url:result'
    # hash
    reqcount = 'spider:hostname:reqcount'
    whitelist = 'spider:domain:whitelist'
    blacklist = 'spider:domain:blacklist'


class MongoConf(object):
    host = '127.0.0.1'
    port = 27017
    username = None
    password = None

    db = 'tspider'
    # collection
    target = 'target' #collection，存放目标站点url
    others = 'others' #collection，存放非目标站点url
```

## 技术细节

### 获取url

获取url采用了两种方式：

- hook拦截资源访问请求
- MutationObserver监控节点和属性变化

拦截资源访问请求，可以监听resource.requested事件，所有请求数据都包含在requestData中；另外还可以在这里拦截广告、统计和静态资源的访问。

```javascript
casper.on('resource.requested', function (requestData, request) {
    //url=requestData.url
});
```

MutationObserver的监听代码可以在page.initialized时进行添加，因为要监听所有节点，所以observe节点为document。

```javascript
casper.on('page.initialized', function (WebPage) {
    WebPage.evaluate(function(){
      var MutationObserver = window.MutationObserver;
      var option = {
          'childList': true,
          'subtree': true,
          'attributes': true,
          'attributeFilter': ['href', 'src']
      };
      var callback = function (records) {
          records.forEach(function (record) {
          // do something
          }
      }
      var mo = new MutationObserver(callback);
      mo.observe(document, option);
    })
});
```

### 数据传递

由于evaluate的执行是在页面scope中，和casperjs的执行scope不在一起，所以数据的传递是一个问题，用window.callPhantom可以从页面返回数据，在casperjs中监听remote.callback事件可以获得数据，但是iframe中不支持window.callPhantom。

console.log不管在mainframe还是childframe中都是可以用的，在casperjs中监听remote.message就可以获得打印的数据，所以可以基于console.log+JSON来传递数据

### 架构

最核心的爬虫功能是用js写的，本身只是个单页爬虫，能抓取当前页面所有的链接。可以单独拿出来运行，路径在core/spider，核心文件是casper_crawler.js和core.js

```bash
Twi1ight at Mac-Pro in ~/Code/TSpider/core/spider (master)
$ casperjs casper_crawler.js
usage: crawler.js http://foo.bar [--output=output.txt] [--cookie=cookie.txt] [--timeout=1000]
Twi1ight at Mac-Pro in ~/Code/TSpider/core/spider (master)
$casperjs casper_crawler.js http://testphp.vulnweb.com/AJAX/index.php --output=out.txt
find 0 iframes
mainframe evaluate
...
remote message caught: events.length  1
remote message caught: string event  javascript:getInfo('infoartist', '1')
remote message caught: got total: 0 forms
remote message caught: events.length  0
mainframe
requests: 20 urls: 29
save urls to out.txt
```

要抓取整站的url，还需要在外面包装一层任务调度。

现在调度器用python实现，任务消息和缓存队列用的redis，爬取结果存储使用mongodb

## 使用

```bash
Twi1ight at Mac-Pro in ~/Code/TSpider (master)
$ python tspider.py
usage:
tspider.py [options] [-u url|-f file.txt]
tspider.py [options] --continue

Yet Another Web Spider

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -u URL, --url URL     Target url, if no tld, only urls in this subdomain
  -f FILE, --file FILE  Load target from file
  --cookie-file FILE    Cookie file from chrome export by EditThisCookie
  --tld                 Crawl all subdomains
  --continue            Continue last task, no init target [-u|-f] need

Worker:
  [optional] options for worker

  -c N, --consumer N    Max number of consumer processes to run, default 5
  -p N, --producer N    Max number of producer processes to run, default 1

Database:
  [optional] options for redis and mongodb

  --mongo-db STRING     Mongodb database name, default "tspider"
  --redis-db NUMBER     Redis db index, N for task queue and N+1 for cache, default 0
```
## TODO

- 添加POST支持
- 保存小于1k的页面内容