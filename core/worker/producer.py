#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
producer
"""
import json

import time

from core.utils.redis_utils import RedisUtils
from core.utils.mongo_utils import MongoUtils
from core.utils.url import URL
from core.utils.log import logger


class Producer(object):
    """
    Producer Class
    make targets for consumer
    save results to mongodb
    """

    def __init__(self, **kwargs):
        """Constructs
        :param tld: scan same top-level-domain subdomains. Scan only subdomain itself when tld=False
        :param mongo_db: mongodb database name.
        :param redis_db: redis db index.
        :param l_url_task: (optional) redis list, where spider get task from
        :param l_url_result: (optional) redis list, where spider save grabbed urls
        :param h_url_saved: (optional) redis hash table, key named by {method}-{url_pattern}, values make no sense
        :param h_domain_whitelist: (optional) redis hash table, domain/hostname in hkeys is allowed to grab
        :param h_domain_blacklist: (optional) redis hash table, domain/subdomain in hkeys is not allowed to grab
        :param h_hostname_reqcount: (optional) redis hash table, key named by hostname, url grabbed count in value
        :return: :class:Producer object
        :rtype: Producer
        """
        kwargs.setdefault('tld', True)
        kwargs.setdefault('redis_db', 0)

        self.tld = kwargs.get('tld')
        self.mongo_db = kwargs.pop('mongo_db', 'tspider')
        self.__kwargs = kwargs.copy()
        self.redis_utils = RedisUtils(**kwargs)

    def produce(self):
        # mongodb with multipleprocessing must be init after fork
        self.mongo_utils = MongoUtils(database=self.mongo_db)
        if not self.redis_utils.connected or not self.mongo_utils.connected:
            logger.error('no redis/mongodb connection found! exit.')
            return

        while True:
            try:
                _, req = self.redis_utils.fetch_one_result()
                logger.debug('got req, %d results left' % self.redis_utils.result_counts)
                self.proc_req(req)
            except:
                logger.exception('produce exception!')
                if not self.redis_utils.connected:
                    logger.error('redis disconnected! reconnecting...')
                    self.redis_utils = RedisUtils(**self.__kwargs)
                if not self.mongo_utils.connected:
                    logger.error('mongodb disconnected! reconnecting...')
                    self.mongo_utils = MongoUtils(database=self.mongo_db)
                time.sleep(10)

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

        # save to mongodb
        data.update({'pattern': url.url_pattern,
                     'hostname': url.hostname,
                     'domain': url.domain
                     })

        method = data.get('method', '')
        if not method:
            logger.error('not method found!')
            return

        target = self.redis_utils.is_target(url)

        if not self.redis_utils.is_url_saved(method, url):
            logger.debug('redis saved pattern not found!')
            self.mongo_utils.save(data, is_target=target)
            self.redis_utils.set_url_saved(method, url)
        else:
            logger.debug('redis saved pattern found!')

        if not target:
            logger.debug('%s is not target' % (url.domain if self.tld else url.hostname))
            return

        # todo post req
        if method == 'POST':
            logger.debug('POST not support now')
        elif method == 'GET':
            # new host found, add index page to task queue
            if self.redis_utils.get_hostname_reqcount(url.hostname) == 0:
                self.redis_utils.create_task_from_url(URL(url.index_page), add_whitelist=False)
            # check url validation inside create_url_task
            self.redis_utils.create_task_from_url(url, add_whitelist=False)
        else:
            # not GET nor POST
            logger.error('HTTP Verb %s found!' % method)
            logger.debug(data)

    def create_task_from_file(self, fileobj):
        """
        create task from file
        :param filename:
        :return:
        """
        with fileobj:
            for line in fileobj:
                line = line.strip()
                if not line: continue
                url = URL(line)
                self.redis_utils.create_task_from_url(url)


if __name__ == '__main__':
    # tld=False, only scan links inside demo.aisec.cn
    # no scan www.aisec.cn even got links from demo.aisc.cn
    p = Producer(tld=False)
    url = URL('http://demo.aisec.cn/demo/aisec/')
    p.redis_utils.create_task_from_url(url)
    p.produce()

    # with open('test.txt') as f:
    #     p.create_file_task(f)
