#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
producer
"""
import json
import urlparse

import re
import redis
from log import logger
from settings import Redis
from url_utils import URL

r = redis.StrictRedis(host=Redis.host, port=Redis.port,
                      db=0, password=Redis.password)


class Producer(object):
    def __init__(self, redis_db=0, task_queue='spider:task', result_queue='spider:result'):
        """
        :param task_queue:
        :param result_queue:
        :return:
        """
        self.redis = redis.StrictRedis(host=Redis.host, port=Redis.port,
                                       db=redis_db, password=Redis.password)
        self.task_queue = task_queue
        self.result_queue = result_queue
        try:
            self.redis.ping()
        except:
            logger.exception('connect to redis failed!')
            self.redis = None

    def produce(self):
        if not self.redis:
            logger.error('no redis connection found! exit.')
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
        # todo store to mongodb
        #
        url = URL(urlstring)
        pattern = url.get_pattern()
        hashset = '{}://{}'.format(url.scheme, url.netloc)
        if self.redis.hexists(hashset, pattern):
            logger.info('%s already scanned, skip' % url.urlstring)
        else:
            # filter js img etc.
            if url.is_block_ext():
                logger.info('block ext found: %s' % url.urlstring)
                return
            if url.hostname != 'demo.aisec.cn':
                logger.error('not demo.aisec.cn')
                return
            if data.get('method', '') == 'GET':
                self.redis.lpush(self.task_queue, url.urlstring)
            else:
                # todo post req
                pass

    def create_task(self, filename):
        # todo  create task from file
        pass


if __name__ == '__main__':
    p = Producer()
    p.produce()
