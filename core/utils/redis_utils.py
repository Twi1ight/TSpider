#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
redis_task
"""
import redis
from settings import RedisConf, MAX_URL_REQUEST_PER_SITE
from core.utils.log import logger


class RedisUtils(object):
    def __init__(self, redis_db=0, task_queue='spider:task', result_queue='spider:result',
                 domain_queue='spider:targetdomain', reqcount_queue='spider:reqcount',
                 saved_queue='spider:saved', tld=True):
        self.redis_task = redis.StrictRedis(host=RedisConf.host, port=RedisConf.port,
                                            db=redis_db, password=RedisConf.password)
        cache_db = (redis_db + 1) % 15
        # redis handle for cached url pattern
        self.redis_cache = redis.StrictRedis(host=RedisConf.host, port=RedisConf.port,
                                             db=cache_db, password=RedisConf.password)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.domain_queue = domain_queue
        self.reqcount_queue = reqcount_queue
        self.saved_queue = saved_queue
        self.tld = tld
        try:
            self.redis_task.ping()
        except:
            logger.exception('connect to redis failed!')
            self.redis_task = None

    @property
    def connected(self):
        return True if self.redis_task else False

    def fetch_one_result(self, timeout=0):
        return self.redis_task.brpop(self.result_queue, timeout)

    @property
    def task_counts(self):
        return self.redis_task.llen(self.result_queue)

    def set_url_saved(self, method, url):
        """
        :param method:
        :param url: URL class instance
        :return:
        """
        pattern = url.store_pattern_redis(method)
        self.redis_cache.hsetnx(self.saved_queue, pattern, '*')

    def is_url_saved(self, method, url):
        """
        :param method:
        :param url: URL class instance
        :return:
        """
        pattern = url.store_pattern_redis(method)
        return self.redis_cache.hexists(self.saved_queue, pattern)

    def incr_hostname_reqcount(self, hostname):
        self.redis_task.hincrby(self.reqcount_queue, hostname, 1)

    def get_hostname_reqcount(self, hostname):
        # fixed on 2016-08-04
        # hget return string if exists key else None
        count = self.redis_task.hget(self.reqcount_queue, hostname)
        return int(count) if count else 0

    def set_url_scanned(self, url):
        """
        :param url: URL class instance
        :return:
        """
        self.redis_cache.hsetnx(url.scanned_table, url.spider_pattern, '*')

    def is_url_scanned(self, url):
        """
        :param url: URL class instance
        :return:
        """
        return self.redis_cache.hexists(url.scanned_table, url.spider_pattern)

    def is_target(self, url):
        """
        :param url: URL class instance
        :return:
        """
        if self.tld:
            return self.redis_task.hexists(self.domain_queue, url.domain)
        else:
            return self.redis_task.hexists(self.domain_queue, url.hostname)

    def add_targetdomain(self, url):
        """
        :param url: URL class instance
        :return:
        """
        if self.tld:
            self.redis_task.hsetnx(self.domain_queue, url.domain, '*')
        else:
            self.redis_task.hsetnx(self.domain_queue, url.hostname, '*')

    def create_url_task(self, url, set_target=True):
        """
        :param url: URL class instance
        :param set_target: for init scan task, disabled in task result produce
        :return:
        """
        if not self.valid_task_url(url): return

        logger.info('add task: %s' % url.urlstring)
        self.redis_task.lpush(self.task_queue, url.urlstring)
        # add targetdomain
        if set_target: self.add_targetdomain(url)
        # set scanned hash table
        self.set_url_scanned(url)
        # incr req count
        self.incr_hostname_reqcount(url.hostname)

    def valid_task_url(self, url):
        """
        :param url: URL class instance
        :return:
        """
        # filter js img etc.
        if not url.valid or url.blocked:
            logger.debug('invalid url or extention')
            return False

        # filter for alicdn url:
        # http://m.alicdn.com/home-node/4.0.18/??css/reset.css,css/common.css,css/header.css
        if url.path.endswith('/') and url.querystring.startswith('?'):
            logger.debug('alicdn file: %s' % url.urlstring)
            return False

        # check scanned
        if self.is_url_scanned(url):
            logger.debug('%s already scanned, skip' % url.urlstring)
            return False

        if self.get_hostname_reqcount(url.hostname) > MAX_URL_REQUEST_PER_SITE:
            logger.debug('%s max req count reached!' % url.hostname)
            return False

        return True
