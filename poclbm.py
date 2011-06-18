#!/usr/bin/python

import sys

if sys.version_info < (2, 7):
  print 'Sorry: you must use Python 2.7'
  sys.exit(1)

import argparse
import re

import pyopencl as cl
from time import sleep
from BitcoinMiner import *

PROGRAM_VERSION = '0.0.1'

class Device(object):
  
  TYPE_UNKNOWN  = 'Unknown'
  TYPE_CPU_C    = 'CPU (c)'
  TYPE_CPU_SSE2 = 'CPU (SSE2)'
  TYPE_OPENCL   = 'OpenCL'
  
  def __init__(self, name, number, type_=TYPE_UNKNOWN):
    self._name = name
    self._number = number
    self._type = type_
  
  def getName(self):
    return self._name
  
  def getNumber(self):
    return self._number
  
  def getType(self):
    return self._type
  
  def __str__(self):
    return 'Device "({numnber} {name})" of type "{type_}"'.format(
      name=self.name,
      number=self.number,
      type_=self._type
    )

class CpuDevice(Device):
  
  def __init__(self, name, number, cpuNumber, sse=False, sse2=False):
    if sse2:
      Device.__init__(self, name, number, Device.TYPE_CPU_SSE2)
    else:
      Device.__init__(self, name, number, Device.TYPE_CPU_C)
    self._cpuNumber = cpuNumber
    self.sse  = sse
    self.sse2 = sse2

class OpenCLDevice(Device):
  
  def __init__(self, name, number, openCl):
    Device.__init__(self, name, number, Device.TYPE_OPENCL)
    self._openCl = openCl

class DeviceList(object):
  
  def __init__(self):
    self._devices = []
    self._populateOpenCl()
    self._populateCpus()
    
  def __len__(self):
    return len(self._devices)

  def showAllDevices(self):
    print '#  | Type       | Name'
    print '---+------------+--' + '-'*30
    for device in self._devices:
      print '{num:<2} | {type_:<10} | {name}'.format(
        num=device.getNumber(),
        type_=device.getType(),
        name=device.getName()
      )
    print '---+------------+--' + '-'*30
  
  def _populateOpenCl(self):
    for device in cl.get_platforms():
      self._devices.append( OpenCLDevice(device.name, len(self._devices), device) )
  
  def _populateCpus(self):
    try:
      proc = open("/proc/cpuinfo", "r")
    except IOError as e:
      self._cpus.append( Cpu("Unknown (Only assumed)", 0) )
      return
    
    sse  = False
    sse2 = False
    for line in proc:
      if line == "\n":
        cpu = CpuDevice(name, len(self._devices), number, sse=sse, sse2=sse2)
        self._devices.append(cpu)
        sse  = False
        sse2 = False
        continue
      match = re.match('processor\t*: (?P<number>[0-9]+)', line)
      if  match != None:
        number = match.group("number")
        continue
      
      match = re.match('model name\t*: (?P<name>.*)$', line)
      if  match != None:
        name = match.group("name")
        continue
      
      match = re.match('flags\t*: (?P<flags>.*)$', line)
      if  match != None:
        flags = match.groups("flags")[0].split(" ")
        for flag in flags:
          if flag == "sse":
            sse = True
          elif flag == "sse2":
            sse2 = True
        continue
  

if __name__ == '__main__':
  
  parser = argparse.ArgumentParser(
    description='A OpenCL client for BitCoin minning',
    epilog='See http://www.xyz.com/abs for more'
  )
  
  #parser.add_argument('--version',      action='version', version=USER_AGENT)
  parser.add_argument('--version',      action='version', version='OpenPyCoiner Version '+PROGRAM_VERSION)
  parser.add_argument(
    '--user',
    action='store',
    nargs='?',
    default='bitcoin',
    type=str,
    help='User name',
    dest='user'
  )
  parser.add_argument(
    '--password',
    action='store',
    nargs='?',
    default='password',
    type=str,
    help='Password',
    dest='password'
  )
  parser.add_argument(
    '--host',
    action='store',
    nargs='?',
    default='localhost',
    type=str,
    help='Address to the server',
    dest='host'
  )
  parser.add_argument(
    '--port',
    action='store',
    nargs='?',
    default=8332,
    type=int,
    help='Server port number',
    dest='port'
  )
  parser.add_argument(
    '--secure',
    action='store_true',
    help='Force https (SSL) connection',
    dest='secure'
  )
  parser.add_argument(
    '--device',
    action='store',
    nargs='?',
    default=0,
    type=int,
    help='Device number, see --list for a list of devices',
    dest='device'
  )
  parser.add_argument(
    '--list',
    action='store_true',
    help='List all devices',
    dest='list'
  )
  parser.add_argument(
    '--verbose',
    action='store_true',
    help='Show alot of rubish',
    dest='verbose'
  )
  
  """
  parser.add_option('-r', '--rate',     dest='rate',     default=1,           help='hash rate display interval in seconds, default=1', type='float')
  parser.add_option('-f', '--frames',   dest='frames',   default=30,          help='will try to bring single kernel execution to 1/frames seconds, default=30, increase this for less desktop lag', type='int')
  parser.add_option('-a', '--askrate',  dest='askrate',  default=5,           help='how many seconds between getwork requests, default 5, max 10', type='int')
  parser.add_option('-w', '--worksize', dest='worksize', default=-1,          help='work group size, default is maximum returned by opencl', type='int')
  parser.add_option('-v', '--vectors',  dest='vectors',  action='store_true', help='use vectors')
  parser.add_option('-s', '--sleep',    dest='frameSleep', default=0,         help='sleep per frame in seconds, default 0', type='float')
  parser.add_option('--backup',         dest='backup',   default=None,        help='use fallback pools: user:pass@host:port[,user:pass@host:port]')
  parser.add_option('--tolerance',      dest='tolerance',default=2,           help='use fallback pool only after N consecutive connection errors, default 2', type='int')
  parser.add_option('--failback',       dest='failback', default=2,           help='attempt to fail back to the primary pool every N getworks, default 2', type='int')
  """
  
  args = parser.parse_args()
  
  if args.port < 0 or args.port > 0xFFFF:
    print 'Invalid port (0 <= port => 4,294,967,296)'
    parser.print_usage()
    sys.exit(1)
  
  devices = DeviceList()
  
  if args.list:
    devices.showAllDevices()
    sys.exit(0)
  
  # more than 1 device and non selected
  if args.device < 0 or args.device >= len(devices):
    print 'Please select a real device (0 to %d)' % (len(devices)-1)
    devices.showAllDevices()
    sys.exit(1)
  
  sys.exit(0)
  ## TODO ##########################################################

  devices = platforms[args.platform].get_devices()

  miner = None
  try:
    miner = BitcoinMiner(
              devices[args.device],
              #args.backup,
              #args.tolerance,
              #args.failback,
              args.host,
              args.user,
              args.password,
              args.port,
              #args.frames,
              #args.rate,
              #args.askrate,
              #args.worksize,
              #args.vectors,
              #args.verbose,
              #args.frameSleep
            )
    miner.mine()
  except KeyboardInterrupt:
    print '\nCtrl-C\nexiting ...'
  finally:
    if miner:
      miner.exit()
  sleep(1.1)
