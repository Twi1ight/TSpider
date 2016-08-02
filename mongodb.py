#!/usr/bin/python
# -*- coding:utf-8 -*-
#
# -----------------------------------------------------------
# Author:      chensongnian@baidu.com
# Created:     16/8/1 下午7:33
# Copyright:   (c) 2016 Baidu.com, Inc. All Rights Reserved
# -----------------------------------------------------------
"""
mongodb
"""
from log import logger
from settings import MongoConf
from pymongo import MongoClient


class MongoUtils(object):
    def __init__(self, database='tspider', target_collection='targetresult',
                 other_collection='otheresult'):
        try:
            self._client = MongoClient('mongodb://{}:{}'.format(MongoConf.host, MongoConf.port))
            self._client.server_info()
            self._target = self._client[database][target_collection]
            self._other = self._client[database][other_collection]
        except:
            logger.exception('connect mongodb failed!')
            self._client = None

    def save(self, reqdict, is_target=True):
        if not self._client or self.exists(reqdict, is_target):
            return
        try:
            handle = self._target if is_target else self._other
            result = handle.insert_one(reqdict)
            if result.acknowledged:
                logger.debug('insert success: %s' % str(result.inserted_id))
                return
            logger.error('insert failed: %s' % reqdict['url'])
        except:
            logger.exception('mongodb save exception!')

    def exists(self, reqdict, is_target=True):
        if not self._client:
            return False
        try:
            query = {'method': reqdict.get('method', ''),
                     'pattern': reqdict.get('pattern', '')}
            handle = self._target if is_target else self._other
            cursor = handle.find(query, limit=1)
            if cursor.count() > 0:
                logger.debug('document exists: %s-%s' % (query['method'], query['pattern']))
                return True
            else:
                return False
        except:
            logger.exception('mongodb exists excepiton!')
            return False


if __name__ == '__main__':
    c = MongoUtils()
    c.save({'test': 'test1'})
    print c.exists({'test': 'test1'})
    c.save({'test': 'test2'})
    c.save({'test1': 'test3'})
