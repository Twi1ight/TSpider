#TSpider
Yet an other dynamic web spider.

##0x01 Baics
Spider component based on [http://blog.wils0n.cn/?post=18](http://blog.wils0n.cn/?post=18) by [wils0n](http://blog.wils0n.cn)  
With redis as task MQ, and save all urls to mongodb  

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
`spider:targetdomain` [*hash*] domains allow to spider, domain not in this hashtable won't be grab  
`spider:reqcount` [*hash*]  record request count for each domain  
`spider:saved` [*hash*] record url pattern which has saved to mongodb

**mongodb**  
`tspider` databass  
`tspider.targetresult`  collection  
`tspider.otheresult` collection

##0x0x TODO  

* add post url as task
