#!/usr/bin/python
# -*- coding:utf-8 -*-
#
# -----------------------------------------------------------
# Author:      chensongnian@baidu.com
# Created:     16/8/1 下午5:57
# Copyright:   (c) 2016 Baidu.com, Inc. All Rights Reserved
# -----------------------------------------------------------
"""
url_utils
"""
import re
import urlparse


class URL(object):
    BLOCKEXT = ['a3c', 'ace', 'aif', 'aifc', 'aiff', 'arj', 'asf', 'asx', 'attach', 'au',
                'avi', 'bin', 'cab', 'cache', 'class', 'djv', 'djvu', 'dwg', 'es', 'esl',
                'exe', 'fif', 'fvi', 'gz', 'hqx', 'ice', 'ief', 'ifs', 'iso', 'jar', 'kar',
                'mid', 'midi', 'mov', 'movie', 'mp', 'mp2', 'mp3', 'mp4', 'mpeg', '7z',
                'mpeg2', 'mpg', 'mpg2', 'mpga', 'msi', 'pac', 'pdf', 'ppt', 'pptx', 'psd',
                'qt', 'ra', 'ram', 'rm', 'rpm', 'snd', 'svf', 'tar', 'tgz', 'tif', 'gzip',
                'tiff', 'tpl', 'uff', 'wav', 'wma', 'wmv', 'doc', 'docx', 'db', 'jpg', 'png',
                'bmp', 'svg', 'gif', 'jpeg', 'css', 'js', 'cur', 'ico', 'zip', 'txt', 'apk',
                'dmg']

    def __init__(self, url):
        self.urlstring = url
        self._p = urlparse.urlsplit(url)
        if not self._p.scheme and not self._p.netloc:
            self.is_url = False
        self.is_url = True

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
    def path(self):
        return self._p.path

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
        return dict(urlparse.parse_qsl(self._p.query, keep_blank_values=True))

    @property
    def fragment(self):
        return self._p.fragment

    def get_pattern(self):
        """
        :param urlstring:
        :return:
        """
        path_pattern = re.sub('\d+', 'd+', self._p.path)
        query_params = '<>'.join(sorted(self.querydict.keys()))
        pattern = '{}?{}'.format(path_pattern, query_params)
        return pattern

    def is_block_ext(self):
        return True if self.extension in URL.BLOCKEXT else False


if __name__ == '__main__':
    print URL(
            'http://www.baidu.com/fuck/kjskdjf.php?args=kjsdfu&k=kuc&iiii=ksnc#skdf').get_pattern()
