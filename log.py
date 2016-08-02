#!/usr/bin/python
# -*- coding:utf-8 -*-
#
# -----------------------------------------------------------
# Author:      chensongnian@baidu.com
# Created:     16/8/1 下午4:37
# Copyright:   (c) 2016 Baidu.com, Inc. All Rights Reserved
# -----------------------------------------------------------
"""
log.py
"""

import os
import logging
import logging.handlers


class Logger(object):
    __slots__ = ('logger')

    logger = None

    def __init__(self, log_path='log/tspider', level=logging.INFO, when="D", backup=7,
                 format="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(message)s",
                 datefmt="%Y-%m-%d %H:%M:%S"):
        Logger.logger = self._init(log_path, level, when, backup, format, datefmt)

    @staticmethod
    def _init(log_path='log/tspider', level=logging.INFO, when="D", backup=7,
              format="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(message)s",
              datefmt="%Y-%m-%d %H:%M:%S"):
        """
        init_log - initialize log module

        Args:
          log_path      - Log file path prefix.
                          Log data will go to two files: log_path.log and log_path.log.wf
                          Any non-exist parent directories will be created automatically
          level         - msg above the level will be displayed
                          DEBUG < INFO < WARNING < ERROR < CRITICAL
                          the default value is logging.INFO
          when          - how to split the log file by time interval
                          'S' : Seconds
                          'M' : Minutes
                          'H' : Hours
                          'D' : Days
                          'W' : Week day
                          default value: 'D'
          format        - format of the log
                          default format:
                          %(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(message)s
                          INFO: 2016-12-09 18:02:42: log.py:40 * HELLO WORLD
          backup        - how many backup file to keep
                          default value: 7

        Raises:
            OSError: fail to create log directories
            IOError: fail to open log file
        """
        formatter = logging.Formatter(format, datefmt)
        logger = logging.getLogger('tspider')
        logger.setLevel(level)

        dir = os.path.dirname(log_path)
        if not os.path.isdir(dir):
            os.makedirs(dir)

        handler = logging.handlers.TimedRotatingFileHandler(log_path + ".log",
                                                            when=when,
                                                            backupCount=backup)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger


logger = Logger(level=logging.DEBUG).logger
