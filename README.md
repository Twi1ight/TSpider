# TSpider

简单来讲，这货是一个动态web爬虫

## 背景

基于CasperJS和PhantomJS，所以可以自动渲染网页、动态解析js，支持ajax和各种乱七八糟的前端交互。

代码基于[phantomjs爬虫小记](http://blog.wils0n.cn/?post=18) by [wils0n](http://blog.wils0n.cn) ，在tuicool上也有这篇文章[http://www.tuicool.com/articles/JbEfIvV](http://www.tuicool.com/articles/JbEfIvV) ， 原作者的代码在Github上也有[crawler_phantomjs](https://github.com/wilson9x1/crawler_phantomjs)

我在其基础上，增强了交互功能，修复了一些问题，新增了一些功能。

功能：

- 自动填充和提交表单
- 从文件载入cookie
- 过滤广告和统计链接
- 过滤静态资源访问
- 载入cookie后防注销和登出
- 支持各种on*交互事件


## 技术细节

window.callPhantom  remote.callback 不支持iframe  