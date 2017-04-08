#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2016/8/14 11:29

Copyright (c) 2016-2017 twi1ight@t00ls.net (http://twi1ight.com/)
See the file 'doc/COPYING' for copying permission
"""
import sys

sys.path.append('../')
import argparse
from collections import defaultdict
from core.utils.url import URL


def cmdparse():
    parse = argparse.ArgumentParser(usage='%(prog)s -i urls.txt -o urls4poc.txt')
    parse.add_argument('-i', dest='infile', metavar='FILE', help='urls file')
    parse.add_argument('-o', dest='outfile', metavar='FILE', help='processed url file, remove similar url')
    parse.add_argument('-p', dest='printf', action='store_true', help='print result on console')
    args = parse.parse_args()
    if not args.infile:
        parse.exit(parse.format_help())
    return args


def process(filename):
    data = defaultdict(dict)
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            url = URL(line)
            if not url.valid: continue
            netloc = url.netloc
            pattern = url.pattern
            if pattern not in data[netloc]:
                data[netloc][pattern] = url.urlstring
    return data


if __name__ == '__main__':
    args = cmdparse()
    data = process(args.infile)
    outf = open(args.outfile, 'w') if args.outfile else None
    for netloc in data:
        for url in data[netloc].itervalues():
            if args.printf: print url
            if outf: outf.write(url + '\n')
    if outf: outf.close()
