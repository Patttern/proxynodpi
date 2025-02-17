# -*- coding: utf-8 -*-

import random
import asyncio
from logging_handler import initLogger
import timeit


__author__ = "Egor Babenko"
__copyright__ = "Copyright 2025"
__credits__ = []
__license__ = "LGPL"
__version__ = "1.0.10"
__updated__ = "2025-02-15"
__maintainer__ = "Egor Babenko"
__email__ = "patttern@gmail.com"
__status__ = "Development"


class ProxyServer():
  def __init__(self, host:str=None, port:int=8881, debug:bool=False, show_logs:bool=False, show_stats:bool=False):
    self.log = initLogger(self)
    self.blockedlistFile = 'blacklist.txt'
    self.tasks:list = list()
    self.bufferSize:int = 4096
    self.host:str = host
    self.port:int = port
    self.debug:bool = debug
    self.showLogs:bool = show_logs
    self.showStats:bool = show_stats
    self.conns:int = 0
    self.globConns:int = 0
    self.datas:int = 0
    self.globDatas:int = 0
    self.chunks:int = 0
    self.globChunks:int = 0
    self.start = timeit.default_timer()
    asyncio.run(self.main())

  async def connect(self, localReader, localWriter):
    httpData = await localReader.read(self.bufferSize)
    peer = localWriter.get_extra_info('peername')
    if self.showLogs:
      self.log.info(f'New connection: {len(httpData)} => {httpData}')

    try:
      type, target = httpData.split(b"\r\n")[0].split(b" ")[0:2]
      host, port = target.split(b":")
    except:
      localWriter.close()
      return

    if type != b"CONNECT":
      localWriter.close()
      return

    localWriter.write(b'HTTP/1.1 200 OK\n\n')
    await localWriter.drain()

    try:
      self.log.info(f'[{peer[0]}:{peer[1]}] Try connect to {host}:{port}')
      remote_reader, remote_writer = await asyncio.open_connection(host, port)
    except:
      localWriter.close()
      return

    self.start = timeit.default_timer()
    self.conns += 1
    self.globConns += self.conns
    if self.showLogs:
      self.log.info(f'localReader: {localReader}')
      self.log.info(f'localWriter: {localWriter}')
    if port == b'443':
      await self.fragment(localReader, remote_writer)

    sender = asyncio.create_task(self.pipe(localReader, remote_writer))
    receiver = asyncio.create_task(self.pipe(remote_reader, localWriter))
    if self.debug:
      self.tasks.append(sender)
      self.tasks.append(receiver)
      if self.showLogs:
        self.log.info(f'Tasks size: {len(self.tasks)}')

  async def fragment(self, localReader, remoteWriter):
    self.datas += 1
    self.globDatas += self.datas
    if self.showLogs:
      self.log.info(f'localReader: {localReader}')
      self.log.info(f'remoteWriter: {remoteWriter}')
    try:
      head = await localReader.read(5)
      data = await localReader.read(self.bufferSize)
      if self.showLogs:
        self.log.info('=' * 100)
        self.log.info(f'Header: {head}')
        self.log.info(f'Data ({len(data)}): {data}')
    except Exception as e:
      self.log.warn(f'[NON-CRITICAL ERROR] {e}')
      localReader.close()
      return
    parts:list = list()

    blocked:list = [line.rstrip().encode() for line in open(self.blockedlistFile, 'r', encoding='utf-8')]
    if all([data.find(site) == -1 for site in blocked]):
      remoteWriter.write(head + data)
      await remoteWriter.drain()
      return

    host_end_index = data.find(b"\x00")
    if host_end_index != -1:
      parts.append(bytes.fromhex("1603")
                   + bytes([random.randint(0, 255)])
                   + int(host_end_index + 1).to_bytes(2, byteorder="big")
                   + data[: host_end_index + 1])
      data = data[host_end_index + 1:]

    while data:
      part_len = random.randint(1, len(data))
      chunk = (((bytes.fromhex("1603")
              + bytes([random.randint(0, 255)]))
              + int(part_len).to_bytes(2, byteorder="big"))
              + data[0:part_len])
      if self.showLogs:
        self.log.info('')
        self.log.info(f'Chunk ({len(chunk)}): {chunk}')
      parts.append(chunk)
      data = data[part_len:]
    self.chunks += len(parts)
    self.globChunks += self.chunks
    resultData = b''.join(parts)
    if self.showLogs:
      self.log.info(f'Result data ({len(resultData)}): {resultData}')
    remoteWriter.write(resultData)
    await remoteWriter.drain()

  async def pipe(self, reader, writer):
    if self.showLogs:
      self.log.info(f'reader: {reader}')
      self.log.info(f'writer: {writer}')
    while not reader.at_eof() and not writer.is_closing():
      try:
        writer.write(await reader.read(self.bufferSize))
        await writer.drain()
      except:
        break
    writer.close()
    if self.showStats:
      self.log.info(f'({timeit.default_timer() - self.start}s) Conns: {self.conns}, Datas: {self.datas}, Chunks: {self.chunks}')
      self.log.info(f'[GLOB] Conns: {self.globConns}, Datas: {self.globDatas}, Chunks: {self.globChunks}')
    self.conns:int = 0
    self.datas:int = 0
    self.chunks:int = 0

  async def main(self):
    server = await asyncio.start_server(self.connect, self.host, self.port)
    serverData = server.sockets[1].getsockname()
    runStr:str = f'* ProxyNoDPI v{__version__} ({__updated__}) runned on {serverData[0]}:{serverData[1]} *'
    self.log.info('')
    self.log.info('*' * len(runStr))
    self.log.info(runStr)
    self.log.info('*' * len(runStr))
    await server.serve_forever()
