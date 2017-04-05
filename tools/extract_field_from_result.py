#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2016/8/13 16:59

Copyright (c) 2016-2017 twi1ight@t00ls.net (http://twi1ight.com/)
See the file 'doc/COPYING' for copying permission
"""
import argparse
import json
import sys


def cmdparse():
    parse = argparse.ArgumentParser(usage='%(prog)s -f field -i spider.txt -o outfile')
    parse.add_argument('-f', dest='field', metavar='NAME',
                       help='field to extract from spider result export from mongodb')
    parse.add_argument('-i', dest='infile', metavar='FILE', help='mongoexport spider result file')
    parse.add_argument('-o', dest='outfile', metavar='FILE', help='save field to file')
    parse.add_argument('-p', dest='printf', action='store_true', help='print result on console')
    args = parse.parse_args()
    if not args.field and not args.infile:
        parse.exit(parse.format_help())
    return args


def extract():
    args = cmdparse()
    outf = open(args.outfile, 'w') if args.outfile else None
    with open(args.infile) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            data = json.loads(line)
            if args.field not in data:
                print >> sys.stderr, '{} not in result'.format(args.field)
                sys.exit()
            if args.printf: print data[args.field]
            if outf: outf.write(data[args.field] + '\n')
    if outf: outf.close()


if __name__ == '__main__':
    extract()
