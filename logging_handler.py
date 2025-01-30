#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# Log handler (Lartech)
#
# (C) 2022-2024 Egor Babenko, Saint-Petersburg, Russia
# Released under GNU Lesser General Public License (LGPL)
# email: e.babenko@lar.tech
# --------------------------------------------------------------------


import logging
import logging.handlers


__author__ = "Egor Babenko"
__copyright__ = "Copyright 2025"
__credits__ = []
__license__ = "LGPL"
__version__ = "1.0.0"
__updated__ = "2025-01-29"
__maintainer__ = "Egor Babenko"
__email__ = "e.babenko@lar.tech"
__status__ = "Development"

LOG_FILENAME = 'logs/proxy-nodpi.log'

class ContextFilter(logging.Filter):
  def filter(self, record):
    record.expandedFuncName = '%s.%s' % (record.name, record.funcName)
    return True

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

  fileHandler = logging.FileHandler(filename=LOG_FILENAME, mode='a')
  fileHandler.setLevel(logging.DEBUG)
  fileHandler.setFormatter(formatter)
  logger.addHandler(fileHandler)

  return logger
