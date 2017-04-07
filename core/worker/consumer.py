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


class Consumer(object):
    def __init__(self, **kwargs):
        """
        :return: :class:Consumer object
        :rtype: Consumer
        """
        self.__cookie_file = kwargs.pop('cookie_file')
        self.redis_handle = RedisUtils(tld=kwargs.pop('tld'), db=kwargs.pop('redis_db'))

    def consume(self):
        if not self.redis_handle.connected:
            logger.error('no redis connection found in consumer! exit.')
            return

        while True:
            try:
                url = self.redis_handle.fetch_one_task()
                logger.info('get task url: %s' % url)
                logger.info('%d tasks left' % self.redis_handle.task_counts)
                self.start_spider(url, self.__cookie_file)
            except:
                logger.exception('consumer exception!')
                if not self.redis_handle.connected:
                    logger.error('redis disconnected! reconnecting...')
                    self.redis_handle.connect()
                time.sleep(10)

    def start_spider(self, url, cookie_file=None):
        results = SpiderPage(url, cookie_file=cookie_file).spider()
        for _ in results:
            self.redis_handle.insert_result(_)


if __name__ == '__main__':
    c = Consumer()
    c.consume()
