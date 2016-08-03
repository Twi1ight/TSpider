#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
buil scanned pattern cache for redis from mongodb
"""
from core.utils.mongodb import MongoUtils
from core.utils.redis_utils import RedisUtils
from core.utils.url import URL

# import redis
m = MongoUtils()
r = RedisUtils()


def build_saved_cache():
    for doc in m.query({}, {"_id": 0, "method": 1, "url": 1}):
        url = URL(doc['url'])
        r.set_url_saved(doc['method'], url)

    for doc in m.query({}, {"_id": 0, "method": 1, "url": 1}, is_target=False):
        url = URL(doc['url'])
        r.set_url_saved(doc['method'], url)


def transfer_scanned_cache():
    tables = r.redis_task.keys('http*')
    for hashtable in tables:
        patterns = r.redis_task.hkeys(hashtable)
        for pattern in patterns:
            r.redis_cache.hsetnx(hashtable, pattern, '*')


if __name__ == '__main__':
    build_saved_cache()
    transfer_scanned_cache()
