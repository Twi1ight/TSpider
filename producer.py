#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
producer
"""
import json
import redis
from log import logger
from mongodb import MongoUtils
from settings import RedisConf
from url_utils import URL


class Producer(object):
    """
    Producer Class
    make targets for consumer
    store results to mongodb
    """

    def __init__(self, redis_db=0, task_queue='spider:task', result_queue='spider:result',
                 domain_queue='spider:whitedomain', tld=True):
        """
        :param redis_db:
        :param task_queue:
        :param result_queue:
        :param domain_queue:
        :param tld: scan same top-level-domain subdomains. Scan only subdomain self when tld=False
        :return:
        """

        self.redis = redis.StrictRedis(host=RedisConf.host, port=RedisConf.port,
                                       db=redis_db, password=RedisConf.password)
        self.mongodb = MongoUtils()
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.domain_queue = domain_queue
        self.tld = tld
        try:
            self.redis.ping()
        except:
            logger.exception('connect to redis failed!')
            self.redis = None

    def produce(self):
        if not self.redis or not self.mongodb:
            logger.error('no redis/mongodb connection found! exit.')
            return
        while True:
            _, req = self.redis.brpop(self.result_queue, 0)
            logger.info('got req, %d results left' % self.redis.llen(self.result_queue))
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
        self.mongodb.save(data)

        # check scanned
        if self.is_scanned(url):
            logger.debug('%s already scanned, skip' % url.urlstring)
        else:
            # filter js img etc.
            if url.is_block_ext():
                logger.debug('block ext found: %s' % url.urlstring)
                return
            if not self.is_whitedomain(url):
                logger.debug('%s not white domain' % url.domain)
                return
            if data.get('method', '') == 'GET':
                self.create_url_task(url)
            else:
                # todo post req
                logger.error(data)
                pass

    def set_scanned(self, url):
        """
        :param url: URL class instance
        :return:
        """
        self.redis.hsetnx(url.hashtable, url.spider_pattern, '*')

    def is_scanned(self, url):
        """
        :param url: URL class instance
        :return:
        """
        return self.redis.hexists(url.hashtable, url.spider_pattern)

    def is_whitedomain(self, url):
        """
        :param url: URL class instance
        :return:
        """
        if self.tld:
            return self.redis.hexists(self.domain_queue, url.domain)
        else:
            return self.redis.hexists(self.domain_queue, url.hostname)

    def set_whitedomain(self, url):
        """
        :param url: URL class instance
        :return:
        """
        if self.tld:
            self.redis.hsetnx(self.domain_queue, url.domain, '*')
        else:
            self.redis.hsetnx(self.domain_queue, url.hostname, '*')

    def create_url_task(self, url):
        """
        :param url: URL class instance
        :return:
        """
        self.redis.lpush(self.task_queue, url.urlstring)
        # set scanned hash table
        self.set_scanned(url)

    def create_file_task(self, filename):
        """
        create task from file
        :param filename:
        :return:
        """
        with open(filename) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                url = URL(line)
                if not url.is_url:
                    continue
                self.set_whitedomain(url)
                self.create_url_task(url)


if __name__ == '__main__':
    # tld=False, only scan links inside demo.aisec.cn
    # no scan www.aisec.cn even got links from demo.aisc.cn
    p = Producer(tld=False)
    url = URL('http://demo.aisec.cn/demo/aisec/')
    p.set_whitedomain(url)
    p.create_url_task(url)
    p.produce()
