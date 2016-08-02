#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
producer
"""
import redis
import json
from settings import RedisConf, MAX_URL_REQUEST_PER_SITE
from core.utils.mongodb import MongoUtils
from core.utils.url import URL
from core.utils.log import logger


class Producer(object):
    """
    Producer Class
    make targets for consumer
    store results to mongodb
    """

    def __init__(self, redis_db=0, task_queue='spider:task', result_queue='spider:result',
                 domain_queue='spider:targetdomain', status_queue='spider:status', tld=True):
        """
        :param redis_db:
        :param task_queue:
        :param result_queue:
        :param domain_queue:
        :param status_queue:
        :param tld: scan same top-level-domain subdomains. Scan only subdomain itself when tld=False
        :return:
        """
        self.redis_task = redis.StrictRedis(host=RedisConf.host, port=RedisConf.port,
                                            db=redis_db, password=RedisConf.password)
        cache_db = (redis_db + 1) % 15
        # redis handle for cached url pattern
        self.redis_cache = redis.StrictRedis(host=RedisConf.host, port=RedisConf.port,
                                             db=cache_db, password=RedisConf.password)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.domain_queue = domain_queue
        self.status_queue = status_queue
        self.tld = tld
        try:
            self.redis_task.ping()
        except:
            logger.exception('connect to redis failed!')
            self.redis_task = None

    def produce(self):
        # mongodb with multipleprocessing must be init after fork
        self.mongodb = MongoUtils()
        if not self.redis_task or not self.mongodb.connected:
            logger.error('no redis/mongodb connection found! exit.')
            return

        while True:
            _, req = self.redis_task.brpop(self.result_queue, 0)
            logger.info('got req, %d results left' % self.redis_task.llen(self.result_queue))
            self.proc_req(req)

    def proc_req(self, req):
        try:
            data = json.loads(req)
        except:
            logger.exception('json loads req error: %s' % req)
            return
        urlstring = data.get('url', '')
        if not urlstring:
            logger.error('empty url found!')
            return
        url = URL(urlstring)

        # store to mongodb
        data.update({'pattern': url.store_pattern,
                     'hostname': url.hostname,
                     'domain': url.domain
                     })
        target = self.is_target(url)
        self.mongodb.save(data, is_target=target)

        if not target:
            logger.debug('%s is not target' % (url.domain if self.tld else url.hostname))
            return

        # filter js img etc.
        if url.is_block_ext():
            logger.debug('block ext found: %s' % url.urlstring)
            return

        # todo post req
        if data.get('method', '') == 'POST':
            logger.debug('POST not support now')
            return

        # check scanned
        if self.is_scanned(url):
            logger.debug('%s already scanned, skip' % url.urlstring)
            return

        if self.get_req_count(url.hostname) > MAX_URL_REQUEST_PER_SITE:
            logger.info('%s max req count reached!' % url.hostname)
            return
        # all is well
        if data.get('method', '') == 'GET':
            self.create_url_task(url)
        else:
            # todo post req
            logger.debug(data)
            pass

    def incr_req_count(self, hostname):
        self.redis_task.hincrby(self.status_queue, hostname, 1)

    def get_req_count(self, hostname):
        return self.redis_task.hget(self.status_queue, hostname)

    def set_scanned(self, url):
        """
        :param url: URL class instance
        :return:
        """
        self.redis_cache.hsetnx(url.hashtable, url.spider_pattern, '*')

    def is_scanned(self, url):
        """
        :param url: URL class instance
        :return:
        """
        return self.redis_cache.hexists(url.hashtable, url.spider_pattern)

    def is_target(self, url):
        """
        :param url: URL class instance
        :return:
        """
        if self.tld:
            return self.redis_task.hexists(self.domain_queue, url.domain)
        else:
            return self.redis_task.hexists(self.domain_queue, url.hostname)

    def set_targetdomain(self, url):
        """
        :param url: URL class instance
        :return:
        """
        if self.tld:
            self.redis_task.hsetnx(self.domain_queue, url.domain, '*')
        else:
            self.redis_task.hsetnx(self.domain_queue, url.hostname, '*')

    def create_url_task(self, url):
        """
        :param url: URL class instance
        :return:
        """
        self.redis_task.lpush(self.task_queue, url.urlstring)
        # set scanned hash table
        self.set_scanned(url)
        # incr req count
        self.incr_req_count(url.hostname)

    def create_file_task(self, fileobj):
        """
        create task from file
        :param filename:
        :return:
        """
        with fileobj:
            for line in fileobj:
                line = line.strip()
                if not line:
                    continue
                url = URL(line)
                if not url.is_url or url.is_block_ext():
                    continue
                self.set_targetdomain(url)
                self.create_url_task(url)


if __name__ == '__main__':
    # tld=False, only scan links inside demo.aisec.cn
    # no scan www.aisec.cn even got links from demo.aisc.cn
    p = Producer(tld=False)
    url = URL('http://demo.aisec.cn/demo/aisec/')
    p.set_targetdomain(url)
    p.create_url_task(url)
    p.produce()

    # with open('test.txt') as f:
    #     p.create_file_task(f)
