#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
Copyright (c) 2016-2017 twi1ight@t00ls.net (http://twi1ight.com/)
See the file 'doc/COPYING' for copying permission
"""
import os
import logging

VERSION = 'v1.9'

MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
SPIDER_PATH = os.path.join(MODULE_PATH, 'core/spider')
TMPDIR_PATH = os.path.join(MODULE_PATH, '.tmp')

LOG_PATH = os.path.join(MODULE_PATH, 'log/tspider.log')
LOG_LEVEL = logging.DEBUG

PSL_FILE_PATH = os.path.join(MODULE_PATH, 'core/utils/public_suffix_list.dat')

MAX_URL_REQUEST_PER_SITE = 100
CASPERJS_TIMEOUT = 120
DEFAULT_CRAWL_TLD = True


class RedisConf(object):
    host = '127.0.0.1'
    port = 6379
    password = None

    db = 0
    # list
    saved = 'spider:url:saved'
    tasks = 'spider:url:task'
    result = 'spider:url:result'
    # hash
    reqcount = 'spider:hostname:reqcount'
    whitelist = 'spider:domain:whitelist'
    blacklist = 'spider:domain:blacklist'


class MongoConf(object):
    host = '127.0.0.1'
    port = 27017
    username = None
    password = None

    db = 'tspider'
    # collection
    target = 'target'
    others = 'others'
