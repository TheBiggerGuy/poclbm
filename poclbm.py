#!/usr/bin/python

import sys

if sys.version_info < (2, 7):
  print 'Sorry: you must use Python 2.7'
  sys.exit(1)

try:
  import pyopencl
  cl = True
except ImportError:
  cl = False

import argparse
import logging

from BitcoinMiner import *
from DeviceFinder import *

PROGRAM_VERSION = 2
PROGRAM_NAME    = 'OpenPyCoiner Version %d' % PROGRAM_VERSION

if __name__ == '__main__':
  
  # start the logging framework
  logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
  log = logging.getLogger("Main")
  
  # first show a list of known warnings
  if not cl:
    print 'WARNING: No OpenCL libary found. Please install "pyOpenCL" to enable GPU prossesing\n'
  if sys.subversion[0] != 'CPython':
    print 'WARNING: Not running on "CPython", this is untested\n'
  
  # set op the argument parser
  parser = argparse.ArgumentParser(
    description='A OpenCL client for BitCoin minning',
    epilog='See https://github.com/TheBiggerGuy/poclbm for more'
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
    nargs='*',
    default=[0],
    type=int,
    help='Device number, see --list for a list of devices',
    dest='devices'
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
  
  # search for all devices
  sysDevices = DeviceList()
  
  # only asked to list devices
  if args.list:
    sysDevices.showAllDevices()
    sys.exit(0)
  
  # invalid device number given
  for device in args.devices:
    if device < 0 or device >= len(sysDevices):
      print 'Please select a real device (0 to %d)' % (len(sysDevices)-1)
      sysDevices.showAllDevices()
      sys.exit(1)
  
  # TODO
  for device in args.devices:
    if sysDevices[device].getType() != Device.TYPE_OPENCL:
      print 'Sorry only OpenCL devices supported currently'
      sysDevices.showAllDevices()
      sys.exit(1)
  
  # Main loop ##################################################################
  print "-"*76
  miners = []
  try:
    # build all the minners
    for device in args.devices:
      miner = BitcoinMiner(
        sysDevices[device].getOpenCL(),
        args.host,
        args.user,
        args.password,
        args.port,
        secure=args.secure,
        userAgentString=PROGRAM_NAME
      )
      miners.append(miner)
    # start all the minners
    for miner in miners:
      miner.mine()
  except KeyboardInterrupt:
    print # try to clean the carret
    log.warn('Ctrl-C - Exiting ...')
    sys.exit(0)
  finally:
    # kill and wait for all the minners to die
    for miner in miners:
      if miner != None:
        miner.exit()
        while not miner.isStopped:
          pass
        log.warn('a minner died :(')
    log.warn('finished')
    print "-"*76
    print "The End"

