#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
buil scanned pattern cache for redis from mongodb
"""
import sys

sys.path.append('../')
from core.utils.mongo_utils import MongoUtils
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


if __name__ == '__main__':
    build_saved_cache()
