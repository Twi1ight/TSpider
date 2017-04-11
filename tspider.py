#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
TSpider is a web spider based on CasperJS and PhantomJS

Copyright (c) 2016-2017 twi1ight@t00ls.net (http://twi1ight.com/)
See the file 'doc/COPYING' for copying permission
"""
import os
import sys
import argparse
from multiprocessing import Process, Value, Lock, Event

from core.utils.log import logger
from core.utils.redis_utils import RedisUtils
from core.utils.url import URL
from core.worker.consumer import Consumer
from core.worker.producer import Producer
from settings import VERSION, RedisConf, MongoConf, TMPDIR_PATH


def cmdparse():
    parser = argparse.ArgumentParser(usage='\n%(prog)s [options] [-u url|-f file.txt]'
                                           '\n%(prog)s [options] --continue',
                                     description='Yet Another Web Spider',
                                     version=VERSION)
    parser.add_argument('-u', '--url', dest='url',
                        help='Target url, if no tld, only urls in this subdomain')
    parser.add_argument('-f', '--file', dest='file', type=open,
                        help='Load target from file')
    parser.add_argument('--cookie-file', dest='cookie_file', metavar='FILE',
                        help='Cookie file from chrome export by EditThisCookie')
    parser.add_argument('--tld', action='store_true', dest='tld',
                        help='Crawl all subdomains')
    parser.add_argument('--continue', dest='keepon', action='store_true',
                        help='Continue last task, no init target [-u|-f] need')
    worker = parser.add_argument_group(title='Worker', description='[optional] options for worker')
    worker.add_argument('-c', '--consumer', metavar='N', type=int, default=5, dest='consumer',
                        help='Max number of consumer processes to run, default 5')
    worker.add_argument('-p', '--producer', metavar='N', type=int, default=1, dest='producer',
                        help='Max number of producer processes to run, default 1')
    db = parser.add_argument_group(title='Database', description='[optional] options for redis and mongodb')
    db.add_argument('--mongo-db', metavar='STRING', dest='mongo_db', default=MongoConf.db,
                    help='Mongodb database name, default "tspider"')
    db.add_argument('--redis-db', metavar='NUMBER', dest='redis_db', type=int, default=RedisConf.db,
                    help='Redis db index, default 0')
    args = parser.parse_args()
    if not any([args.url, args.file, args.keepon]):
        parser.exit(parser.format_help())
    return args


if __name__ == '__main__':
    args = cmdparse()
    redis_handle = RedisUtils(db=args.redis_db)
    if args.keepon:
        redis_handle.restore_startup_params(args)
        logger.info(args)

    for f in os.listdir(TMPDIR_PATH):
        os.remove(os.path.join(TMPDIR_PATH, f))
    tspider_context = {}
    tspider_context['live_spider_counts'] = Value('i', 0)
    tspider_context['task_done'] = Event()
    tspider_context['lock'] = Lock()
    kwargs = {'tld': args.tld, 'cookie_file': args.cookie_file,
              'redis_db': args.redis_db, 'mongo_db': args.mongo_db}
    for _ in range(args.consumer):
        worker = Consumer(**kwargs).consume
        proc = Process(name='consumer-%d' % _, target=worker, args=(tspider_context,))
        proc.daemon = True
        proc.start()
    for _ in range(args.producer):
        worker = Producer(**kwargs).produce
        proc = Process(name='producer-%d' % _, target=worker, args=(tspider_context,))
        proc.daemon = True
        proc.start()

    if not args.keepon:
        redis_handle.flushdb()
        redis_handle.save_startup_params(args)
        target = args.url or args.file
        producer = Producer(**kwargs)
        if isinstance(target, basestring):
            url = URL(target)
            if not url.valid or url.blocked:
                logger.error('not valid url, exit.')
                sys.exit(-1)
            producer.create_task_from_url(url)
        # file object
        else:
            producer.create_task_from_file(target)

    redis_handle.close()
    tspider_context['task_done'].wait()
