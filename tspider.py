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


def cmdparse():
    parser = argparse.ArgumentParser(usage='%(prog)s [options]',
                                     description='A web spider',
                                     version='1.0')
    parser.add_argument('-c', '--consumer', metavar='N', type=int, default=1, dest='consumer',
                        help='consumers to run')
    parser.add_argument('-p', '--producer', metavar='N', type=int, default=1, dest='producer',
                        help='producers to run')
    parser.add_argument('-u', '--url', dest='url',
                        help='target url, if no tld, only urls in this subdomain')
    parser.add_argument('-f', '--file', dest='file', type=open,
                        help='load target from file')
    parser.add_argument('--tld', action='store_true', dest='tld',
                        help='spider all subdomains')
    arg = parser.parse_args()
    if not any([arg.url, arg.file]):
        parser.exit(parser.format_help())
    return arg


if __name__ == '__main__':
    arg = cmdparse()
    target = arg.url or arg.file
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

    producer = Producer(tld=tld_enable)
    if isinstance(target, basestring):

        url = URL(target)
        if not url.is_url or url.is_block_ext():
            logger.error('not valid url, exit.')
            sys.exit(-1)
        producer.set_targetdomain(url)
        producer.create_url_task(url)
    # file object
    else:
        with target:
            producer.create_file_task(target)

    map(lambda x: x.join(), consumer_pool)
    map(lambda x: x.join(), producer_pool)
