#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
consumer
"""
import time

import redis
from core.spider.spider import SpiderPage
from core.utils.log import logger
from settings import RedisConf


# r = redis.StrictRedis(host=Redis.host, port=Redis.port,
#                       db=Redis.db, password=Redis.password)
# r.lpush()


class Consumer(object):
    def __init__(self, redis_db=0, task_queue='spider:task', result_queue='spider:result'):
        """
        :param task_queue:
        :param result_queue:
        :return:
        """
        self.redis = redis.StrictRedis(host=RedisConf.host, port=RedisConf.port,
                                       db=redis_db, password=RedisConf.password)
        self.task_queue = task_queue
        self.result_queue = result_queue
        try:
            self.redis.ping()
        except:
            logger.exception('connect to redis failed!')
            self.redis = None

    def consume(self):
        if not self.redis:
            logger.error('no redis connection found! exit.')
            return

        while True:
            _, url = self.redis.brpop(self.task_queue, 0)
            logger.info('get task url: %s' % url)
            logger.info('%d tasks left' % self.redis.llen(self.task_queue))
            self.start_spider(url)
            time.sleep(3)

    def start_spider(self, url):
        results = SpiderPage(url).spider()
        for _ in results:
            self.redis.lpush(self.result_queue, _)


if __name__ == '__main__':
    c = Consumer()
    c.consume()
