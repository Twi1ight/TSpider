#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
Copyright (c) 2016-2017 twi1ight@t00ls.net (http://twi1ight.com/)
See the file 'doc/COPYING' for copying permission
"""
import redis
from settings import RedisConf, MAX_URL_REQUEST_PER_SITE
from core.utils.log import logger


class RedisUtils(object):
    def __init__(self, db=RedisConf.db, tld=False):
        """
        :param tld: scan same top-level-domain subdomains. Scan only subdomain itself when tld=False.
        :param db: redis db number.
        :return: :class:RedisUtils object
        :rtype: RedisUtils
        """
        self.db = db
        self.tld = tld
        self.l_url_tasks = RedisConf.tasks
        self.l_url_result = RedisConf.result
        self.h_url_saved = RedisConf.saved
        self.h_url_scanned = RedisConf.scanned
        self.h_whitelist = RedisConf.whitelist
        self.h_blocklist = RedisConf.blocklist
        self.h_hostname_reqcount = RedisConf.reqcount
        self.h_startup_params = RedisConf.startup_params
        self.redis_client = None
        self.connect()

    @property
    def connected(self):
        try:
            self.redis_client.ping()
            return True
        except:
            logger.exception('connect to redis failed!')
            return False

    def connect(self):
        try:
            self.redis_client = redis.StrictRedis(host=RedisConf.host, port=RedisConf.port,
                                                  db=self.db, password=RedisConf.password,
                                                  socket_keepalive=True)
        except:
            logger.exception('connect redis failed!')

    def close(self):
        self.redis_client.connection_pool.disconnect()

    def fetch_one_task(self, timeout=0):
        """
        :param timeout: default 0, block mode
        :return:
        """
        _, url = self.redis_client.brpop(self.l_url_tasks, timeout)
        return url

    def fetch_one_result(self, timeout=0):
        """
        :param timeout: default 0, block mode
        :return:
        """
        return self.redis_client.brpop(self.l_url_result, timeout)

    @property
    def result_counts(self):
        """
        :return: The total number of left results
        """
        return self.redis_client.llen(self.l_url_result)

    @property
    def task_counts(self):
        """
        :return: The total number of left tasks
        """
        return self.redis_client.llen(self.l_url_tasks)

    def insert_result(self, result):
        self.redis_client.lpush(self.l_url_result, result)

    def set_url_saved(self, method, url):
        """
        :param method:
        :param url: URL class instance
        :return:
        """
        key = '{}-{}'.format(method, url.pattern)
        self.redis_client.hsetnx(self.h_url_saved, key, '*')

    def is_url_saved(self, method, url):
        """
        :param method:
        :param url: URL class instance
        :return:
        """
        key = '{}-{}'.format(method, url.pattern)
        return self.redis_client.hexists(self.h_url_saved, key)

    def incr_hostname_reqcount(self, hostname):
        self.redis_client.hincrby(self.h_hostname_reqcount, hostname, 1)

    def get_hostname_reqcount(self, hostname):
        # fixed on 2016-08-04
        # hget return string if key exists else None
        count = self.redis_client.hget(self.h_hostname_reqcount, hostname)
        return int(count) if count else 0

    def set_url_scanned(self, url):
        """
        :param url: URL class instance
        :return:
        """
        key = '{}/{}'.format(url.netloc, url.path_querystring_pattern)
        self.redis_client.hsetnx(self.h_url_scanned, key, '*')

    def is_url_scanned(self, url):
        """
        :param url: URL class instance
        :return:
        """
        key = '{}/{}'.format(url.netloc, url.path_querystring_pattern)
        return self.redis_client.hexists(self.h_url_scanned, key)

    def is_target(self, url):
        """
        :param url: URL class instance
        :return:
        """
        if self.tld:
            return self.redis_client.hexists(self.h_whitelist, url.domain)
        else:
            return self.redis_client.hexists(self.h_whitelist, url.hostname)

    def insert_to_whitelist(self, url):
        """
        :param url: URL class instance
        :return:
        """
        if self.tld:
            self.redis_client.hsetnx(self.h_whitelist, url.domain, '*')
        else:
            self.redis_client.hsetnx(self.h_whitelist, url.hostname, '*')

    def create_task_from_url(self, url, add_whitelist=True, valid_url_check=True):
        """
        :param url: URL class instance
        :param valid_url_check: disable valid task url check when re-create task during add blackdomain in runtime
        :param add_whitelist: for init scan task, disabled in task result produce
        :return:
        """
        if valid_url_check and not self.valid_task_url(url): return

        logger.info('add task: %s' % url.urlstring)
        self.redis_client.lpush(self.l_url_tasks, url.urlstring)
        # add targetdomain
        if add_whitelist: self.insert_to_whitelist(url)
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

        if self.is_blocked(url):
            logger.debug('%s is blacklist domain!' % url.hostname)
            return False

        return True

    def is_blocked(self, url):
        """
        :param url: :class:URL object
        :return: bool
        :rtype: bool
        """
        hostname, domain = url.hostname, url.domain
        if self.redis_client.hexists(self.h_blocklist, domain): return True
        if hostname == domain: return False

        # a.b.c.d.test.com => a.b.c.d
        prefix = hostname[:-(len(domain) + 1)]
        prefix_splits = prefix.split('.')
        # a.b.c.d.test.com => ['a.b.c.d.test.com', 'b.c.d.test.com', 'c.d.test.com', 'd.test.com']
        for i in range(len(prefix_splits)):
            pre = '.'.join(prefix_splits[i:])
            name = '{}.{}'.format(pre, domain)
            if self.redis_client.hexists(self.h_blocklist, name): return True
        return False

    def add_blocklist(self, dnsname):
        """
        :param dnsname:
        :return:
        """
        self.redis_client.hsetnx(self.h_blocklist, dnsname, '*')

    def save_startup_params(self, args):
        self.redis_client.hset(self.h_startup_params, 'tld', args.tld)
        self.redis_client.hset(self.h_startup_params, 'cookie_file', args.cookie_file)
        self.redis_client.hset(self.h_startup_params, 'consumer', args.consumer)
        self.redis_client.hset(self.h_startup_params, 'producer', args.producer)
        self.redis_client.hset(self.h_startup_params, 'mongo_db', args.mongo_db)

    def restore_startup_params(self, args):
        v = self.redis_client.hget(self.h_startup_params, 'tld')
        args.tld = True if v == 'True' else False
        v = self.redis_client.hget(self.h_startup_params, 'cookie_file')
        args.cookie_file = None if v == 'None' else v
        args.consumer = int(self.redis_client.hget(self.h_startup_params, 'consumer'))
        args.producer = int(self.redis_client.hget(self.h_startup_params, 'producer'))
        args.mongo_db = self.redis_client.hget(self.h_startup_params, 'mongo_db')

    def flushdb(self):
        self.redis_client.flushdb()
