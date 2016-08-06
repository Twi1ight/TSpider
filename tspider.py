#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
TSpider main file
"""
import sys
import argparse
from multiprocessing import Pool, Process

from core.utils.log import logger
from core.utils.url import URL
from core.worker.consumer import Consumer
from core.worker.producer import Producer
from settings import VERSION


def cmdparse():
    parser = argparse.ArgumentParser(usage='\n%(prog)s [options] [-u url|-f file.txt]'
                                           '\n%(prog)s [options] --continue',
                                     description='A web spider',
                                     version=VERSION)
    parser.add_argument('-u', '--url', dest='url',
                        help='target url, if no tld, only urls in this subdomain')
    parser.add_argument('-f', '--file', dest='file', type=open,
                        help='load target from file')
    parser.add_argument('--tld', action='store_true', dest='tld',
                        help='spider all subdomains')
    parser.add_argument('--continue', dest='keepon', action='store_true',
                        help='continue last task, no init target [-u|-f] need')
    worker = parser.add_argument_group(title='Worker', description='opionts for worker')
    worker.add_argument('-c', '--consumer', metavar='N', type=int, default=1, dest='consumer',
                        help='consumers to run')
    worker.add_argument('-p', '--producer', metavar='N', type=int, default=1, dest='producer',
                        help='producers to run')
    arg = parser.parse_args()
    if not any([arg.url, arg.file, arg.keepon]):
        parser.exit(parser.format_help())
    return arg


if __name__ == '__main__':
    arg = cmdparse()
    tld_enable = arg.tld
    producer_pool = []
    consumer_pool = []
    for _ in range(arg.consumer):
        proc = Process(name='consumer-%d' % _, target=Consumer().consume)
        proc.start()
        consumer_pool.append(proc)
    for _ in range(arg.producer):
        proc = Process(name='producer-%d' % _, target=Producer(tld=tld_enable).produce)
        proc.start()
        producer_pool.append(proc)

    if not arg.keepon:
        target = arg.url or arg.file
        producer = Producer(tld=tld_enable)
        if isinstance(target, basestring):

            url = URL(target)
            if not url.is_url or url.is_block_ext():
                logger.error('not valid url, exit.')
                sys.exit(-1)
            producer.redis_utils.create_url_task(url)
        # file object
        else:
            with target:
                producer.create_file_task(target)

    map(lambda x: x.join(), consumer_pool)
    map(lambda x: x.join(), producer_pool)
