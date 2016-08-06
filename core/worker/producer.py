#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
producer
"""
import json

from core.utils.redis_utils import RedisUtils
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
                 domain_queue='spider:targetdomain', reqcount_queue='spider:reqcount',
                 saved_queue='spider:saved', tld=True):
        """
        :param redis_db:
        :param task_queue:
        :param result_queue:
        :param domain_queue:
        :param reqcount_queue:
        :param tld: scan same top-level-domain subdomains. Scan only subdomain itself when tld=False
        :return:
        """
        self.redis_utils = RedisUtils(redis_db, task_queue, result_queue, domain_queue,
                                      reqcount_queue, saved_queue, tld)
        self.tld = tld

    def produce(self):
        # mongodb with multipleprocessing must be init after fork
        self.mongodb = MongoUtils()
        if not self.redis_utils.connected or not self.mongodb.connected:
            logger.error('no redis/mongodb connection found! exit.')
            return

        while True:
            _, req = self.redis_utils.fetch_one_result()
            logger.debug('got req, %d results left' % self.redis_utils.task_counts)
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
        data.update({'pattern': url.store_pattern_mongodb,
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
            self.mongodb.save(data, is_target=target)
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
            # check url validation inside create_url_task
            self.redis_utils.create_url_task(url, set_target=False)
        else:
            # todo post req
            logger.debug(data)
            pass

    def create_file_task(self, fileobj):
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
                self.redis_utils.create_url_task(url)


if __name__ == '__main__':
    # tld=False, only scan links inside demo.aisec.cn
    # no scan www.aisec.cn even got links from demo.aisc.cn
    p = Producer(tld=False)
    url = URL('http://demo.aisec.cn/demo/aisec/')
    p.redis_utils.create_url_task(url)
    p.produce()

    # with open('test.txt') as f:
    #     p.create_file_task(f)
