#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
buil scanned pattern cache for redis from mongodb
"""
import sys

sys.path.append('../')
from core.utils.mongodb import MongoUtils
from core.utils.redis_utils import RedisUtils
from core.utils.url import URL

reload(sys)
sys.setdefaultencoding('utf-8')
m = MongoUtils()
r = RedisUtils()


def build_saved_cache():
    for doc in m.query({}, {"_id": 0, "method": 1, "url": 1}):
        url = URL(doc['url'])
        r.set_url_saved(doc['method'], url)

    for doc in m.query({}, {"_id": 0, "method": 1, "url": 1}, is_target=False):
        url = URL(doc['url'])
        r.set_url_saved(doc['method'], url)


def convert_scanned_cache():
    keys = r.redis_cache.keys('http*')
    for old_key in keys:
        u = URL(old_key)
        new_key = u.scanned_table
        cached_pattern = r.redis_cache.hvals(old_key)
        for pattern in cached_pattern:
            r.redis_cache.hsetnx(new_key, pattern or '/', '*')


if __name__ == '__main__':
    build_saved_cache()
    # convert_scanned_cache()