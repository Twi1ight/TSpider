#TSpider
Yet an other dynamic web spider.

##0x01 Baics
TSpider is a web spider based on CasperJS and PhantomJS
Idea based on [http://blog.wils0n.cn/?post=18](http://blog.wils0n.cn/?post=18) by [wils0n](http://blog.wils0n.cn)
The article is also available here: [http://www.tuicool.com/articles/JbEfIvV](http://www.tuicool.com/articles/JbEfIvV)
and the original code : [crawler_phantomjs](https://github.com/wilson9x1/crawler_phantomjs)

I rewrite the code, fix some bugs and add some extra features, it now supports load cookie from file.
With Redis as task MQ, and save all urls to MongoDB
**requirements**  

* casperjs
* phantomjs
* redis
* mongodb
* python 2.7.x

**python module**  

- publicsuffix == 1.1.0  
- pymongo == 3.3.0  
- redis == 2.10.5  

##0x02 Settings  
Most settings are inside *settings.py*  
	
	LOG_LEVEL = logging.DEBUG
	MAX_URL_REQUEST_PER_SITE = 100

	class RedisConf(object):
	    host = '127.0.0.1'
	    port = 6379
	    password = None

	class MongoConf(object):
	    host = '127.0.0.1'
	    port = 27017
	    username = None
	    password = None

**logging**  
Currently logger is file size rotating, default backup count is 3.    
modify `custom_logger` function to customize it

**redis**  
There are 5 list/hashtable in redis  
`spider:task` [*list*] task queue, producer will put target into this list  
`spider:result` [*list*] cache spider result  
`spider:targetdomain` [*hash*] domains whitelist allow to crawl, Domain names that not in this list will not crawl
`spider:reqcount` [*hash*]  record request count for each domain  
`spider:saved` [*hash*] record url pattern which has saved to mongodb

**mongodb**  
`tspider` databass  
`tspider.targetresult`  collection  
`tspider.otheresult` collection

##0x0x TODO  

* add post url as task
* save response body which size <= 1k