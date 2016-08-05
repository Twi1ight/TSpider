#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
settings
"""
import os
import logging

VERSION = 'v1.4'

MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
SPIDER_PATH = os.path.join(MODULE_PATH, 'core/spider')
TMPDIR_PATH = os.path.join(MODULE_PATH, '.tmp')

LOG_PATH = os.path.join(MODULE_PATH, 'log/tspider.log')
LOG_LEVEL = logging.DEBUG

PSL_FILE_PATH = os.path.join(MODULE_PATH, 'core/utils/public_suffix_list.dat')

MAX_URL_REQUEST_PER_SITE = 100


class RedisConf(object):
    host = '127.0.0.1'
    port = 6379
    password = None


class MongoConf(object):
    host = '127.0.0.1'
    port = 27017
    username = None
    password = None
