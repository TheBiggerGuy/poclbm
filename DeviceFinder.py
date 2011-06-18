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

import re

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
  
  def getOpenCL(self):
    return self._openCl

class DeviceList(object):
  
  def __init__(self):
    self._devices = []
    self._populateOpenCl()
    self._populateCpus()
  
  def __getitem__(self, key):
    if type(key) != type(int()):
      raise TypeError("Indexed by int")
    if key < 0 or key >= len(self._devices):
      raise IndexError("Index out of range")
    return self._devices[key]
    
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
    for platform in cl.get_platforms():
      for device in platform.get_devices():
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
  print "This is only a module and can not be run as a program"

