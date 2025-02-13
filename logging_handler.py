# -*- coding: utf-8 -*-

import os
from datetime import datetime
import gzip
import logging
import logging.handlers


__author__ = "Egor Babenko"
__copyright__ = "Copyright 2025"
__credits__ = []
__license__ = "LGPL"
__version__ = "1.0.2"
__updated__ = "2025-02-13"
__maintainer__ = "Egor Babenko"
__email__ = "patttern@gmail.com"
__status__ = "Development"


LOG_FILENAME:str = 'logs/proxy-nodpi.log'
LOG_DATETIME_FORMAT:str = '%Y-%m-%d-%H%M%S'


class GZipRotator:
  def __call__(self, source, dest):
    dest += '.' + datetimeToDateFormat(datetime.now(), LOG_DATETIME_FORMAT)
    os.rename(source, dest)
    f_in = open(dest, 'rb')
    f_out = gzip.open("%s.gz" % dest, 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    os.remove(dest)

class ContextFilter(logging.Filter):
  def filter(self, record):
    record.expandedFuncName = '%s.%s' % (record.name, record.funcName)
    return True

def datetimeToDateFormat(dtsource, format:str) -> str:
  return dtsource.strftime(format)

def initLogger(target, specFormat=None):
  logFormat = '%(asctime)s %(levelname)-7s [%(threadName)-10s] %(expandedFuncName)-20.20s : %(message)s'

  logger = logging.getLogger(target.__class__.__name__)
  logger.setLevel(logging.DEBUG)
  filter = ContextFilter()
  logger.addFilter(filter)
  logger.handlers = []
  logger.propagate = 0

  formatter = logging.Formatter(specFormat if specFormat not in ('', None) else logFormat)

  consoleHandler = logging.StreamHandler()
  consoleHandler.setLevel(logging.INFO)
  consoleHandler.setFormatter(formatter)
  logger.addHandler(consoleHandler)

  fileHandler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, 'midnight', 1, backupCount=7)
  fileHandler.setLevel(logging.DEBUG)
  fileHandler.setFormatter(formatter)
  fileHandler.rotator = GZipRotator()
  logger.addHandler(fileHandler)

  return logger
