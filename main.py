#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from datetime import datetime
import gzip
from logging_handler import LOG_FILENAME
from proxyserver import ProxyServer


__author__ = "Egor Babenko"
__copyright__ = "Copyright 2025"
__credits__ = []
__license__ = "LGPL"
__version__ = "1.0.6"
__updated__ = "2025-02-09"
__maintainer__ = "Egor Babenko"
__email__ = "patttern@gmail.com"
__status__ = "Development"


def datetimeToDateFormat(dtsource, format:str) -> str:
  return dtsource.strftime(format)

def checkAndArchLog():
  LOG_DATETIME_FORMAT:str = '%Y-%m-%d-%H%M%S'
  os.path.isdir(Path(LOG_FILENAME).absolute().parent) or os.mkdir(Path(LOG_FILENAME).absolute().parent)
  if os.path.isfile(LOG_FILENAME):
    gzName = LOG_FILENAME + '.' + datetimeToDateFormat(datetime.now(), LOG_DATETIME_FORMAT)
    with open(LOG_FILENAME, 'rb') as f_in, gzip.open(f'{gzName}.gz', 'wb') as f_out:
      f_out.writelines(f_in)
  open(LOG_FILENAME, 'w').close()

if __name__ == '__main__':
  # Operation with log files
  checkAndArchLog()
  """
  # Set '127.0.0.1' if you need to listen localhost only, otherwise any incomming connection. By default: None
  host='127.0.0.1'
  # Listen any free port. By default: 8881
  port=8881
  # Enable DEBUG if needed. By default: False
  debug=True
  # Show logs if needed. By default: False
  show_logs=True
  # Show statistics if needed. By default: False
  show_stats=True
  # Run with parameters
  ProxyServer(host='127.0.0.1', port=8881, debug=True, show_logs=True, show_stats=True)
  """
  ProxyServer()
