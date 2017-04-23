#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2016/8/7 16:17
add blacklist domain or subdomain in runtime

Copyright (c) 2016-2017 twi1ight@t00ls.net (http://twi1ight.com/)
See the file 'doc/COPYING' for copying permission
"""
import sys

from core.utils.redis_utils import RedisUtils

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'usage: block_domain.py db target.com'
        sys.exit()
    db = int(sys.argv[1])
    domain = sys.argv[2]
    r = RedisUtils(db=db)
    r.add_blocklist(domain)
    print 'add success!'
