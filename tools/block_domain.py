#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2016/8/7 16:17
add blacklist domain or subdomain in runtime

Copyright (c) 2016-2017 twi1ight@t00ls.net (http://twi1ight.com/)
See the file 'doc/COPYING' for copying permission
"""
import sys
import traceback

from core.utils.url import URL
from core.utils.redis_utils import RedisUtils


def remove_from_tasklist(domain):
    urls = []
    while True:
        try:
            urlstring = r.fetch_one_task(timeout=3)
            url = URL(urlstring)
            if r.is_blocked(url):
                continue
            urls.append(urlstring)
        except:
            break

    for url in urls:
        r.create_task_from_url(URL(url), add_whitelist=False, valid_url_check=False)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'usage: block_domain.py db target.com'
        sys.exit()
    db = int(sys.argv[1])
    domain = sys.argv[2]
    r = RedisUtils(db=db)
    r.add_blocklist(domain)

    if r.redis_task.hexists(r.h_blocklist, domain):
        remove_from_tasklist(domain)
        print 'add success!'
    else:
        print 'add failed!'
