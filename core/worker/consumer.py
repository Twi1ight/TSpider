#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
Copyright (c) 2016-2017 twi1ight@t00ls.net (http://twi1ight.com/)
See the file 'doc/COPYING' for copying permission
"""
import time

from core.spider.spider import SpiderPage
from core.utils.log import logger
from core.utils.redis_utils import RedisUtils
from settings import RedisConf


class Consumer(object):
    def __init__(self, **kwargs):
        """
        :param redis_db: redis db index. N for task queue and N+1 for cache.
        :param cookie_file: cookie file used for spider, export from chrome by EditThisCookie plugin
        :return:
        """
        kwargs.setdefault('redis_db', RedisConf.db)
        self.__cookie_file = kwargs.pop('cookie_file', None)
        self.__kwargs = kwargs.copy()
        self.redis_utils = RedisUtils(**kwargs)

    def consume(self):
        if not self.redis_utils.connected:
            logger.error('no redis connection found in consumer! exit.')
            return

        while True:
            try:
                url = self.redis_utils.fetch_one_task()
                logger.info('get task url: %s' % url)
                logger.info('%d tasks left' % self.redis_utils.task_counts)
                self.start_spider(url, self.__cookie_file)
            except:
                logger.exception('consumer exception!')
                if not self.redis_utils.connected:
                    logger.error('redis disconnected! reconnecting...')
                    self.redis_utils = RedisUtils(**self.__kwargs)
                time.sleep(10)

    def start_spider(self, url, cookie_file=None):
        results = SpiderPage(url, cookie_file=cookie_file).spider()
        for _ in results:
            self.redis_utils.insert_result(_)


if __name__ == '__main__':
    c = Consumer()
    c.consume()
