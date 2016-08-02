#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
producer
"""
import json
import redis
from settings import RedisConf
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
                 domain_queue='spider:targetdomain', tld=True):
        """
        :param redis_db:
        :param task_queue:
        :param result_queue:
        :param domain_queue:
        :param tld: scan same top-level-domain subdomains. Scan only subdomain itself when tld=False
        :return:
        """
        self.redis = redis.StrictRedis(host=RedisConf.host, port=RedisConf.port,
                                       db=redis_db, password=RedisConf.password)
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
        # mongodb with multipleprocessing must be init after fork
        self.mongodb = MongoUtils()
        if not self.redis or not self.mongodb.connected():
            logger.error('no redis/mongodb connection found! exit.')
            return
        logger.info(self.tld)
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
        target = self.is_target(url)
        self.mongodb.save(data, is_target=target)

        # check scanned
        if self.is_scanned(url):
            logger.debug('%s already scanned, skip' % url.urlstring)
        else:
            if not target:
                logger.debug('%s is not target' % (url.domain if self.tld else url.hostname))
                return
            # filter js img etc.
            if url.is_block_ext():
                logger.debug('block ext found: %s' % url.urlstring)
                return
            if data.get('method', '') == 'GET':
                self.create_url_task(url)
            else:
                # todo post req
                logger.debug(data)
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

    def is_target(self, url):
        """
        :param url: URL class instance
        :return:
        """
        if self.tld:
            return self.redis.hexists(self.domain_queue, url.domain)
        else:
            return self.redis.hexists(self.domain_queue, url.hostname)

    def set_targetdomain(self, url):
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
