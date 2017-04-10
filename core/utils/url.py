#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
Copyright (c) 2016-2017 twi1ight@t00ls.net (http://twi1ight.com/)
See the file 'doc/COPYING' for copying permission
"""
import codecs

import re
import urlparse
from publicsuffix import PublicSuffixList
from settings import PSL_FILE_PATH


class URL(object):
    BLOCKEXT = ['a3c', 'ace', 'aif', 'aifc', 'aiff', 'arj', 'asf', 'asx', 'attach', 'au',
                'avi', 'bin', 'cab', 'cache', 'class', 'djv', 'djvu', 'dwg', 'es', 'esl',
                'exe', 'fif', 'fvi', 'gz', 'hqx', 'ice', 'ief', 'ifs', 'iso', 'jar', 'kar',
                'mid', 'midi', 'mov', 'movie', 'mp', 'mp2', 'mp3', 'mp4', 'mpeg', '7z',
                'mpeg2', 'mpg', 'mpg2', 'mpga', 'msi', 'pac', 'pdf', 'ppt', 'pptx', 'psd',
                'qt', 'ra', 'ram', 'rm', 'rpm', 'snd', 'svf', 'tar', 'tgz', 'tif', 'gzip',
                'tiff', 'tpl', 'uff', 'wav', 'wma', 'wmv', 'doc', 'docx', 'db', 'jpg', 'png',
                'bmp', 'svg', 'gif', 'jpeg', 'css', 'js', 'cur', 'ico', 'zip', 'txt', 'apk',
                'dmg', 'xml', 'jar', 'class', 'torrent']
    BLOCKHOST = ['mirrors.aliyun.com', 'code.taobao.org']
    # PUBLIC_SUFFIX_LIST_URL = 'http://publicsuffix.org/list/public_suffix_list.dat'
    PSL = PublicSuffixList(codecs.open(PSL_FILE_PATH, encoding='utf8'))

    def __init__(self, url):
        self.valid = True
        self.urlstring = self.normalize_url(url)
        if not self.urlstring:
            self.valid = False
        self._p = urlparse.urlparse(self.urlstring)

    @staticmethod
    def normalize_url(url):
        """
        :param url:
        :return:
        """
        # only hostname
        if not '/' in url:
            return 'http://{}'.format(url)
        p = urlparse.urlparse(url)
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
            url = urlparse.urlunparse(('http', p.netloc, p.path or '/',
                                       p.query, p.params, p.fragment))
        return url

    @property
    def scheme(self):
        return self._p.scheme

    @property
    def netloc(self):
        return self._p.netloc

    @property
    def hostname(self):
        return self._p.hostname

    @property
    def domain(self):
        return self.PSL.get_public_suffix(self.hostname)

    @property
    def path(self):
        # http://www.test.com  =>  self._p.path=''
        return self._p.path or '/'

    @property
    def path_without_file(self):
        return self.path[:self.path.rfind('/') + 1]

    @property
    def filename(self):
        return self.path[self.path.rfind('/') + 1:]

    @property
    def extension(self):
        fname = self.filename
        extension = fname[fname.rfind('.') + 1:]
        if extension == fname:
            return ''
        else:
            return extension

    @property
    def querystring(self):
        return self._p.query

    @property
    def querydict(self):
        # remove keep_blank_values=True, as url blow cause duplicate scans
        # /Common/common/captcha?0.610851539997384 => querydict = {'0.610851539997384': ''}
        return dict(urlparse.parse_qsl(self._p.query))

    @property
    def fragment(self):
        return self._p.fragment

    @property
    def index_page(self):
        return urlparse.urljoin(self.urlstring, '/', allow_fragments=False)

    @property
    def pattern(self):
        """
        :return:
        """
        return urlparse.urlunsplit((self.scheme, self.netloc, self.path_querystring_pattern, '', ''))

    @property
    def path_querystring_pattern(self):
        """
        :return:
        """
        # TODO url pattern
        path_pattern = re.sub('\d+', '{digit}', self.path)
        query_params = '<>'.join(sorted(self.querydict.keys()))
        pattern = '{}?{}'.format(path_pattern, query_params) if query_params else path_pattern
        return pattern

    @property
    def blocked(self):
        return True if self.extension.lower() in URL.BLOCKEXT or self.hostname.lower() in URL.BLOCKHOST else False


if __name__ == '__main__':
    urlstring = 'http://www.test.com/fuck/kjskdjf.php?args=kjsdfu&k=kuc&ii=ksc#skdf'
    # urlstring = '//mat1.gtimg.com/www/icon/favicon2.ico'
    url = URL(urlstring)
    print url.path_querystring_pattern
    print url.pattern
