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
    def __init__(self, tld=True,
                 redis_db=0,
                 l_url_task='spider:url:task',
                 l_url_result='spider:url:result',
                 h_url_saved='spider:url:saved',
                 h_domain_whitelist='spider:domain:whitelist',
                 h_domain_blacklist='spider:domain:blacklist',
                 h_hostname_reqcount='spider:hostname:reqcount'):
        """
        redis cache db {(redis_db+1)%15}
        multiple redis hash tables named by hostname and key is url path pattern used for check whether url was visited

        :param tld: scan same top-level-domain subdomains. Scan only subdomain itself when tld=False.
        :param redis_db: redis db number.
        :param l_url_task: (optional) redis list, which spider get urls
        :param l_url_result: (optional) redis list, which spider send result urls
        :param h_url_saved: (optional) redis hash table, key named by {method}-{url_pattern}, values make no sense
        :param h_domain_whitelist: (optional) redis hash table, domain/hostname in hkeys is allowed to scrap
        :param h_domain_blacklist: (optional) redis hash table, domain/subdomain in hkeys is not allowed to scrap
        :param h_hostname_reqcount: (optional) redis hash table, key named by hostname, url scrapped count in value
        :return: :class:RedisUtils object
        :rtype: RedisUtils
        """
        self.redis_task = redis.StrictRedis(host=RedisConf.host, port=RedisConf.port,
                                            db=redis_db, password=RedisConf.password)
        cache_db = (redis_db + 1) % 15
        # redis handle for cached url pattern
        self.redis_cache = redis.StrictRedis(host=RedisConf.host, port=RedisConf.port,
                                             db=cache_db, password=RedisConf.password)
        self.l_url_task = l_url_task
        self.l_url_result = l_url_result
        self.h_url_saved = h_url_saved
        self.h_domain_whitelist = h_domain_whitelist
        self.h_domain_blacklist = h_domain_blacklist
        self.h_hostname_reqcount = h_hostname_reqcount

        self.tld = tld

    @property
    def connected(self):
        try:
            self.redis_task.ping()
            return True
        except:
            logger.exception('connect to redis failed!')
            return False

    def fetch_one_task(self, timeout=0):
        """
        :param timeout: default 0, block mode
        :return:
        """
        _, url = self.redis_task.brpop(self.l_url_task, timeout)
        return url

    def fetch_one_result(self, timeout=0):
        """
        :param timeout: default 0, block mode
        :return:
        """
        return self.redis_task.brpop(self.l_url_result, timeout)

    @property
    def result_counts(self):
        """
        :return: The total number of left results
        """
        return self.redis_task.llen(self.l_url_result)

    @property
    def task_counts(self):
        """
        :return: The total number of left tasks
        """
        return self.redis_task.llen(self.l_url_task)

    def insert_result(self, result):
        self.redis_task.lpush(self.l_url_result, result)

    def set_url_saved(self, method, url):
        """
        :param method:
        :param url: URL class instance
        :return:
        """
        pattern = url.url_pattern_with_method(method)
        self.redis_cache.hsetnx(self.h_url_saved, pattern, '*')

    def is_url_saved(self, method, url):
        """
        :param method:
        :param url: URL class instance
        :return:
        """
        pattern = url.url_pattern_with_method(method)
        return self.redis_cache.hexists(self.h_url_saved, pattern)

    def incr_hostname_reqcount(self, hostname):
        self.redis_task.hincrby(self.h_hostname_reqcount, hostname, 1)

    def get_hostname_reqcount(self, hostname):
        # fixed on 2016-08-04
        # hget return string if exists key else None
        count = self.redis_task.hget(self.h_hostname_reqcount, hostname)
        return int(count) if count else 0

    def set_url_scanned(self, url):
        """
        :param url: URL class instance
        :return:
        """
        self.redis_cache.hsetnx(url.scanned_table, url.path_param_pattern, '*')

    def is_url_scanned(self, url):
        """
        :param url: URL class instance
        :return:
        """
        return self.redis_cache.hexists(url.scanned_table, url.path_param_pattern)

    def is_target(self, url):
        """
        :param url: URL class instance
        :return:
        """
        if self.tld:
            return self.redis_task.hexists(self.h_domain_whitelist, url.domain)
        else:
            return self.redis_task.hexists(self.h_domain_whitelist, url.hostname)

    def add_targetdomain(self, url):
        """
        :param url: URL class instance
        :return:
        """
        if self.tld:
            self.redis_task.hsetnx(self.h_domain_whitelist, url.domain, '*')
        else:
            self.redis_task.hsetnx(self.h_domain_whitelist, url.hostname, '*')

    def create_url_task(self, url, add_whitelist=True, valid_url_check=True):
        """
        :param url: URL class instance
        :param valid_url_check: disable valid task url check when re-create task during add blackdomain in runtime
        :param add_whitelist: for init scan task, disabled in task result produce
        :return:
        """
        if valid_url_check and not self.valid_task_url(url): return

        logger.info('add task: %s' % url.urlstring)
        self.redis_task.lpush(self.l_url_task, url.urlstring)
        # add targetdomain
        if add_whitelist: self.add_targetdomain(url)
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

        if self.is_blacklist_domain(url):
            logger.debug('%s is blacklist domain!' % url.hostname)
            return False

        return True

    def is_blacklist_domain(self, url):
        """
        hostname is in blacklist domain
        :param url: :class:URL object
        :return: bool
        :rtype: bool
        """
        hostname, domain = url.hostname, url.domain
        if self.redis_task.hexists(self.h_domain_blacklist, domain): return True
        if hostname == domain: return False

        # a.b.c.d.test.com => a.b.c.d
        prefix = hostname[:-(len(domain) + 1)]
        prefix_splits = prefix.split('.')
        # a.b.c.d.test.com => ['a.b.c.d.test.com', 'b.c.d.test.com', 'c.d.test.com', 'd.test.com']
        for i in range(len(prefix_splits)):
            pre = '.'.join(prefix_splits[i:])
            name = '{}.{}'.format(pre, domain)
            if self.redis_task.hexists(self.h_domain_blacklist, name): return True
        return False

    def add_blacklist_domain(self, domain):
        """
        :param domain:
        :return:
        """
        self.redis_task.hsetnx(self.h_domain_blacklist, domain, '*')
