#!/usr/bin/python
# -*- coding:utf-8 -*-
#
"""
https://github.com/jruere/multiprocessing-logging
"""
import logging
import logging.handlers
import multiprocessing
import os
import sys
import threading
import traceback
from settings import LOG_PATH, LOG_LEVEL


def install_mp_handler(logger=None):
    """Wraps the handlers in the given Logger with an MultiProcessingHandler.
    :param logger: whose handlers to wrap. By default, the root logger.
    """
    if logger is None:
        logger = logging.getLogger()

    for i, orig_handler in enumerate(list(logger.handlers)):
        handler = MultiProcessingHandler(
                'mp-handler-{0}'.format(i), sub_handler=orig_handler)

        logger.removeHandler(orig_handler)
        logger.addHandler(handler)


class MultiProcessingHandler(logging.Handler):
    def __init__(self, name, sub_handler=None):
        super(MultiProcessingHandler, self).__init__()

        if sub_handler is None:
            sub_handler = logging.StreamHandler()

        self.sub_handler = sub_handler
        self.queue = multiprocessing.Queue(-1)
        self.setLevel(self.sub_handler.level)
        self.setFormatter(self.sub_handler.formatter)
        # The thread handles receiving records asynchronously.
        t = threading.Thread(target=self.receive, name=name)
        t.daemon = True
        t.start()

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self.sub_handler.setFormatter(fmt)

    def receive(self):
        while True:
            try:
                record = self.queue.get()
                self.sub_handler.emit(record)
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except:
                traceback.print_exc(file=sys.stderr)

    def send(self, s):
        self.queue.put_nowait(s)

    def _format_record(self, record):
        # ensure that exc_info and args
        # have been stringified. Removes any chance of
        # unpickleable things inside and possibly reduces
        # message size sent over the pipe.
        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        self.sub_handler.close()
        logging.Handler.close(self)


def time_rotating_handler(formatter, log_path, level, when="D", backup=7):
    """
      when          - how to split the log file by time interval
                      'S' : Seconds
                      'M' : Minutes
                      'H' : Hours
                      'D' : Days
                      'W' : Week day
                      default value: 'D'
      backup        - how many backup file to keep
                      default value: 7
    """
    handler = logging.handlers.TimedRotatingFileHandler(log_path, when=when, backupCount=backup)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


def size_rotating_handler(formatter, log_path, level, maxBytes=100 * 1024 * 1024, backup=3):
    """
    maxBytes: max log file size
    """
    handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=maxBytes, backupCount=backup)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


def custom_logger(log_path='log/tspider.log',
                  level=logging.INFO,
                  format="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d %(processName)s * %(message)s",
                  datefmt="%Y-%m-%d %H:%M:%S"):
    """
    init_log - initialize log module
    """
    formatter = logging.Formatter(format, datefmt)
    logger = logging.getLogger(__package__)
    logger.setLevel(level)

    dir = os.path.dirname(log_path)
    if not os.path.isdir(dir):
        os.makedirs(dir)

    # handler = time_rotating_handler(formatter, log_path, level)
    # logger.addHandler(handler)

    handler = size_rotating_handler(formatter, log_path, level)
    logger.addHandler(handler)

    # logging to console
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = custom_logger(log_path=LOG_PATH, level=LOG_LEVEL)
# if multipleprocessing
install_mp_handler(logger)
