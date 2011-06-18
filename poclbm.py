#!/usr/bin/python

import sys

if sys.version_info < (2, 7):
  print 'Sorry: you must use Python 2.7'
  sys.exit(1)

try:
  import pyopencl as cl
except ImportError:
  print 'Sorry: you must have pyOpenCL installed'
  sys.exit(1)

import argparse

from BitcoinMiner import *
from DeviceFinder import *

PROGRAM_VERSION = 2
PROGRAM_NAME    = 'OpenPyCoiner Version %d' % PROGRAM_VERSION

if __name__ == '__main__':
  
  parser = argparse.ArgumentParser(
    description='A OpenCL client for BitCoin minning',
    epilog='See http://www.xyz.com/abs for more'
  )
  
  parser.add_argument('--version',      action='version', version=PROGRAM_NAME)
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
  
  args = parser.parse_args()
  
  # check port number
  if args.port < 0 or args.port > 0xFFFF:
    print 'Invalid port (0 <= port => 4,294,967,296)'
    parser.print_usage()
    sys.exit(1)
  
  # for a list of all devices
  devices = DeviceList()
  
  # only asked to list devices
  if args.list:
    devices.showAllDevices()
    sys.exit(0)
  
  # invalid device number given
  if args.device < 0 or args.device >= len(devices):
    print 'Please select a real device (0 to %d)' % (len(devices)-1)
    devices.showAllDevices()
    sys.exit(1)
  
  if devices[args.device].getType() != Device.TYPE_OPENCL:
    print "Sorry only OpenCL devices supported currently"
    sys.exit(1)

  device = devices[args.device].getOpenCL()

  miner = None
  try:
    miner = BitcoinMiner(
              device,
              args.host,
              args.user,
              args.password,
              args.port,
              secure=args.secure,
              userAgentString=PROGRAM_NAME
            )
    miner.mine()
  except KeyboardInterrupt:
    print '\nCtrl-C\nexiting ...'
  finally:
    if miner:
      miner.exit()
      while miner.isStopped:
        pass
  print " ... finished\n"
