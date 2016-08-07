#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2016/8/7 16:17
add blacklist domain or subdomain in runtime
"""
import sys

sys.path.append('../')

from core.utils.redis_utils import RedisUtils

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'usage: add_blacklist_domain.py blackdomain.com'
        sys.exit()
    domain = sys.argv[1]
    r = RedisUtils()
    r.add_blacklist_domain(domain)
    if r.redis_task.hexists(r.h_domain_blacklist, domain):
        print 'add success!'
    else:
        print 'add failed!'
