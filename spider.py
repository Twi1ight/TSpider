#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2016/7/27 23:26
"""
from datetime import datetime
import logging
import os
import json
import tempfile
import subprocess
import traceback
import urlparse
import sys
from log import logger
import uuid

reload(sys)
sys.setdefaultencoding('utf-8')


class SpiderPage(object):
    """
    Spider Page
    """

    def __init__(self, url, outfile=None):
        """
        :param url:
        :param outfile:
        :return:
        """
        self._url = self.normalize_url(url)
        self._outfile = outfile
        self._results = []

    @staticmethod
    def normalize_url(url):
        """
        :param url:
        :return:
        """
        # only hostname
        if not '/' in url:
            return 'http://{}'.format(url)
        p = urlparse.urlsplit(url)
        # www.test.com/index.php
        # exclude /xxxxx/index.php
        if not p.netloc:
            if url.startswith('/'):
                # /xxxxx/index.php
                return ''
            else:
                # www.test.com/index.php
                return 'http://{}'.format(url)
        # //www.test.com/index.php
        if not p.scheme:
            url = urlparse.urlunsplit(('http', p.netloc, p.path, p.query, p.fragment))
        return url

    def spider(self):
        if not self._url:
            logger.info('incorrect url format found!')
            return []

        # fptr, spiderfile = tempfile.mkstemp()
        spiderfile = uuid.uuid4().hex
        command = 'casperjs --ignore-ssl-errors=true --ssl-protocol=any ' \
                  'casper_crawler.js "{url}" "{file}"'.format(url=self._url, file=spiderfile)
        try:
            returncode = subprocess.check_call(command, shell=True)
            logger.info('casperjs succeed, return code %d' % returncode)
        except subprocess.CalledProcessError as e:
            logger.error('casperjs failed, return code: %d' % e.returncode)
        except:
            logger.exception('subprocess failed!')

        urls = []
        # with os.fdopen(fptr) as f:
        with open(spiderfile) as f:
            for line in f:
                line = line.strip()
                try:
                    request = json.loads(line)
                except:
                    method, url, postdata, referer = line.split('|||')
                    postdata = '' if postdata == 'null' else postdata
                    headers = {'Referer': referer}
                else:
                    method = request['method']
                    url = request['url']
                    postdata = request.get('postData', '')
                    headers = {}
                    for header in request['headers']:
                        headers[header['name']] = header['value']
                    headers.pop('Content-Length', '')
                    headers.pop('User-Agent', '')
                    headers.pop('Accept', '')
                # check urls fingerprint
                fp = '%s|%s' % (method, url)
                if fp in urls:
                    continue
                urls.append(fp)

                data = {
                    'method': method,
                    'url': url,
                    'postdata': postdata,
                    'headers': headers
                }
                # print json.dumps(data)
                self._results.append(json.dumps(data))
        os.unlink(spiderfile)
        if self._outfile:
            with open(self._outfile, 'w') as f:
                for url in self._results:
                    f.write(url + '\n')
        return self._results


if __name__ == '__main__':
    # url, outfile = sys.argv[1], sys.argv[2]
    # url = sys.argv[1]
    urls = SpiderPage('http://demo.aisec.cn/demo/aisec/', 'aisec.txt').spider()
    # spider('http://192.168.88.128/page.html')
    for u in urls:
        print u
