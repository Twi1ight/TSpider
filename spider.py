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

reload(sys)
sys.setdefaultencoding('utf-8')


class SpiderPage(object):
    """
    Spider Page
    """

    def __init__(self, url, outfile):
        """
        :param url:
        :param outfile:
        :return:
        """
        self.url = self.normalize_url(url)
        self.outfile = outfile
        self.spider()

    @staticmethod
    def normalize_url(url):
        """
        :param url:
        :return:
        """
        p = urlparse.urlsplit(url)
        if not p.netloc:
            return ''
        if not p.scheme:
            url = urlparse.urlunsplit(('http', p.netloc, p.path, p.query, p.fragment))
        return url

    def querytask(self):
        """
        get task from AMQ
        :return:
        """
        pass

    def sendresult(self, data):
        """
        send result to redis
        :return:
        """
        pass

    def spider(self):
        if not self.url:
            return

        fptr, spiderfile = tempfile.mkstemp()
        command = 'casperjs --ignore-ssl-errors=true --ssl-protocol=any ' \
                  'casper_crawler.js {url} {file}'.format(url=self.url, file=spiderfile)
        try:
            process = subprocess.check_call(command, shell=True)
            print process
        except subprocess.CalledProcessError as e:
            print 'casperjs failed, return code: %d' % e.returncode
        except:
            traceback.print_exc()

        urls = []
        of = open(self.outfile, 'a')
        with os.fdopen(fptr) as f:
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
                print json.dumps(data)
                of.write(json.dumps(data) + '\n')

        os.unlink(spiderfile)
        of.close()


if __name__ == '__main__':
    # url, outfile = sys.argv[1], sys.argv[2]
    # url = sys.argv[1]
    SpiderPage('http://demo.aisec.cn/demo/aisec/', 'aisec.txt')
    # spider('http://192.168.88.128/page.html')
