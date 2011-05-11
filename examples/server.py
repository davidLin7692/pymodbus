#!/usr/bin/env python

#---------------------------------------------------------------------------# 
# the various server implementations
#---------------------------------------------------------------------------# 
from pymodbus.server.sync import StartTcpServer, StartUdpServer
from pymodbus.server.sync import StartSerialServer
from pymodbus.server.async import StartTcpServer as StartATcpServer
from pymodbus.server.async import StartUdpServer as StartAUdpServer
from pymodbus.server.async import StartSerialServer as StartASerialServer

from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

#---------------------------------------------------------------------------# 
# configure the service logging
#---------------------------------------------------------------------------# 
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

#---------------------------------------------------------------------------# 
# initialize your data store
#---------------------------------------------------------------------------# 
store = ModbusSlaveContext(
    di = ModbusSequentialDataBlock(0, [17]*100),
    co = ModbusSequentialDataBlock(0, [17]*100),
    hr = ModbusSequentialDataBlock(0, [17]*100),
    ir = ModbusSequentialDataBlock(0, [17]*100))
context = ModbusServerContext(slaves=store, single=True)

#---------------------------------------------------------------------------# 
# run the server you want
#---------------------------------------------------------------------------# 
#StartATcpServer(context)
#StartSerialServer(context, port='/dev/ptmx')
StartSerialServer(context, port='/tmp/tty1')
