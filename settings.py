#!/usr/bin/python
# -*- coding:utf-8 -*-
#
# -----------------------------------------------------------
# Author:      chensongnian@baidu.com
# Created:     16/8/1 下午5:04
# Copyright:   (c) 2016 Baidu.com, Inc. All Rights Reserved
# -----------------------------------------------------------
"""
settings
"""


class RedisConf(object):
    host = '127.0.0.1'
    port = 6379
    password = None


class MongoConf(object):
    host = '127.0.0.1'
    port = 27017
    username = None
    password = None
