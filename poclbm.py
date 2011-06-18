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

class Cpu(object):
  
  def __init__(self, name, number, sse=False, sse2=False):
    self.name = name
    self.number = number
    self.sse  = sse
    self.sse2 = sse2
  
  def __str__(self):
    return "CPU '{name}' Object".format(name=self.name)

class Cpus(object):
  
  def __init__(self):
    self._cpus = []
    self._populate()
  
  def _populate(self):
    sse  = False
    sse2 = False
    for line in open("/proc/cpuinfo", "r"):
      if line == "\n":
        cpu = Cpu(name, number, sse=sse, sse2=sse2)
        self._cpus.append(cpu)
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
  
  def get_platforms(self):
    return self._cpus

def showAllDevices():
  i = 0
  gpus = cl.get_platforms()
  for gpu in gpus:
    print '[%d]\tOpenCL\t%s' % (i, gpu.name)
    i+=1
  cpus = Cpus().get_platforms()
  for cpu in cpus:
    if cpu.sse2:
      print '[%d]\tSSE2\t%s' % (i, cpu.name)
    else:
      print '[%d]\tc\t\t%s' % (i, cpu.name)
    i+=1

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
  
  """
  parser.add_option('-r', '--rate',     dest='rate',     default=1,           help='hash rate display interval in seconds, default=1', type='float')
  parser.add_option('-f', '--frames',   dest='frames',   default=30,          help='will try to bring single kernel execution to 1/frames seconds, default=30, increase this for less desktop lag', type='int')
  parser.add_option('-d', '--device',   dest='device',   default=-1,          help='use device by id', type='int')
  parser.add_option('-a', '--askrate',  dest='askrate',  default=5,           help='how many seconds between getwork requests, default 5, max 10', type='int')
  parser.add_option('-w', '--worksize', dest='worksize', default=-1,          help='work group size, default is maximum returned by opencl', type='int')
  parser.add_option('-v', '--vectors',  dest='vectors',  action='store_true', help='use vectors')
  parser.add_option('-s', '--sleep',    dest='frameSleep', default=0,         help='sleep per frame in seconds, default 0', type='float')
  parser.add_option('--backup',         dest='backup',   default=None,        help='use fallback pools: user:pass@host:port[,user:pass@host:port]')
  parser.add_option('--tolerance',      dest='tolerance',default=2,           help='use fallback pool only after N consecutive connection errors, default 2', type='int')
  parser.add_option('--failback',       dest='failback', default=2,           help='attempt to fail back to the primary pool every N getworks, default 2', type='int')
  parser.add_option('--verbose',        dest='verbose',  action='store_true', help='verbose output, suitable for redirection to log file')
  parser.add_option('--platform',       dest='platform', default=-1,          help='use platform by id', type='int')
  """
  
  args = parser.parse_args()
  
  if args.list:
    showAllDevices()
    sys.exit(0)
  
  if args.port < 0 or args.port > 0xFFFF:
    print 'Invalid port (0 <= port => 4,294,967,296)'
    parser.print_usage()
    sys.exit(1)
    
  
  sys.exit(0)
  
  
  
  ## TODO ##########################################################
  
  
  # no openCL devices
  if len(platforms) == 0:
    print 'Sorry no openCL devices found'
    sys.exit(1)
  
  # more than 1 device and non selected
  elif len(platforms) > 1 and args.platform == -1:
    print 'Please select a device'
    showPlatforms()
    sys.exit(1)
  
  # platform number too low or high
  elif args.platform < -1 or args.platform >= len(platforms):
    print 'Invalid platform number'
    showPlatforms()
    sys.exit(1)

  # there is only 1 platform and user didn't specify -> default platform 0
  if args.platform == -1:
    args.platform = 0

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
