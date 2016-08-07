#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
consumer
"""
from core.spider.spider import SpiderPage
from core.utils.log import logger
from core.utils.redis_utils import RedisUtils


class Consumer(object):
    def __init__(self, **kwargs):
        """
        :param redis_db: redis db index. N for task queue and N+1 for cache.
        :return:
        """
        kwargs.setdefault('redis_db', 0)
        self.redis_utils = RedisUtils(**kwargs)

    def consume(self):
        if not self.redis_utils.connected:
            logger.error('no redis connection found in consumer! exit.')
            return

        while True:
            url = self.redis_utils.fetch_one_task()
            logger.info('get task url: %s' % url)
            logger.info('%d tasks left' % self.redis_utils.task_counts)
            self.start_spider(url)
            # time.sleep(3)

    def start_spider(self, url):
        results = SpiderPage(url).spider()
        for _ in results:
            self.redis_utils.insert_result(_)


if __name__ == '__main__':
    c = Consumer()
    c.consume()
