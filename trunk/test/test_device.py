import unittest
from pymodbus.device import *
from pymodbus.mexceptions import *

class SimpleDataStoreTest(unittest.TestCase):
    '''
    This is the unittest for the pymod.mexceptions module
    '''

    def setUp(self):
        info = {
                0x00: 'Bashwork',               # VendorName
                0x01: 'PTM',                    # ProductCode
                0x02: '1.0',                    # MajorMinorRevision
                0x03: 'http://internets.com',   # VendorUrl
                0x04: 'pymodbus',               # ProductName
                0x05: 'bashwork',               # ModelName
                0x06: 'unittest',               # UserApplicationName
                0x07: 'x',                      # reserved
                0x08: 'x',                      # reserved
                0x10: 'private'                 # private data
        }
        self.ident   = ModbusDeviceIdentification(info)
        self.control = ModbusControlBlock()
        self.access  = ModbusAccessControl()
        self.control.reset()

    def tearDown(self):
        ''' Cleans up the test environment '''
        del self.ident
        del self.control
        del self.access

    def testUpdateIdentity(self):
        ''' Test device identification reading '''
        self.control.Identity.update(self.ident)
        self.assertEqual(self.control.Identity.vendor_name, "Bashwork")
        self.assertEqual(self.control.Identity.user_application_name, "unittest")

    def testBasicCommands(self):
        ''' Test device identification reading '''
        self.assertEqual(str(self.ident),   "DeviceIdentity")
        self.assertEqual(str(self.control), "ModbusControl")

    def testModbusDeviceIdentificationGet(self):
        ''' Test device identification reading '''
        self.assertEqual(self.ident[0x00], 'Bashwork')
        self.assertEqual(self.ident[0x01], 'PTM')
        self.assertEqual(self.ident[0x02], '1.0')
        self.assertEqual(self.ident[0x03], 'http://internets.com')
        self.assertEqual(self.ident[0x04], 'pymodbus')
        self.assertEqual(self.ident[0x05], 'bashwork')
        self.assertEqual(self.ident[0x06], 'unittest')
        self.assertNotEqual(self.ident[0x07], 'x')
        self.assertNotEqual(self.ident[0x08], 'x')
        self.assertEqual(self.ident[0x10], 'private')
        self.assertEqual(self.ident[0x54], '')

    def testModbusDeviceIdentificationSet(self):
        ''' Test a device identification writing '''
        self.ident[0x07] = 'y'
        self.ident[0x08] = 'y'
        self.ident[0x10] = 'public'
        self.ident[0x54] = 'testing'

        self.assertNotEqual('y', self.ident[0x07])
        self.assertNotEqual('y', self.ident[0x08])
        self.assertEqual('public', self.ident[0x10])
        self.assertEqual('testing', self.ident[0x54])

    def testModbusControlBlockAsciiModes(self):
        ''' Test a server control block ascii mode '''
        self.assertEqual(id(self.control), id(ModbusControlBlock()))
        self.control.Mode = 'RTU'
        self.assertEqual('RTU', self.control.Mode)
        self.control.Mode = 'FAKE'
        self.assertNotEqual('FAKE', self.control.Mode)

    def testModbusControlBlockCounters(self):
        ''' Tests the MCB counters methods '''
        self.assertEqual(0x0, self.control.Counter.BusMessage)
        for i in range(10):
            self.control.Counter.BusMessage += 1
            self.control.Counter.SlaveMessage += 1
        self.assertEqual(10, self.control.Counter.BusMessage)
        self.control.Counter.BusMessage = 0x00
        self.assertEqual(0,  self.control.Counter.BusMessage)
        self.assertEqual(10, self.control.Counter.SlaveMessage)
        self.control.Counter.reset()
        self.assertEqual(0, self.control.Counter.SlaveMessage)

    def testModbusControlBlockCounterSummary(self):
        ''' Tests retrieving the current counter summary '''
        self.assertEqual(0x00, self.control.Counter.summary())
        for i in range(10):
            self.control.Counter.BusMessage += 1
            self.control.Counter.SlaveMessage += 1
            self.control.Counter.SlaveNAK += 1
            self.control.Counter.BusCharacterOverrun += 1
        self.assertEqual(0xa9, self.control.Counter.summary())
        self.control.Counter.reset()
        self.assertEqual(0x00, self.control.Counter.summary())

    def testModbusControlBlockListen(self):
        ''' Tests the MCB listen flag methods '''
        self.assertEqual(self.control.ListenOnly, False)
        self.control.ListenOnly = not self.control.ListenOnly
        self.assertEqual(self.control.ListenOnly, True)

    def testModbusControlBlockDelimiter(self):
        ''' Tests the MCB delimiter setting methods '''
        self.assertEqual(self.control.Delimiter, '\r')
        self.control.Delimiter = '='
        self.assertEqual(self.control.Delimiter, '=')
        self.control.Delimiter = 61
        self.assertEqual(self.control.Delimiter, '=')

    def testModbusControlBlockDiagnostic(self):
        ''' Tests the MCB delimiter setting methods '''
        self.assertEqual([False] * 16, self.control.getDiagnosticRegister())
        for i in [1,3,4,6]:
            self.control.setDiagnostic({i:True});
        self.assertEqual(True, self.control.getDiagnostic(1))
        self.assertEqual(False, self.control.getDiagnostic(2))
        actual = [False, True, False, True, True, False, True] + [False] * 9
        self.assertEqual(actual, self.control.getDiagnosticRegister())
        for i in range(16):
            self.control.setDiagnostic({i:False});

    def testModbusControlBlockInvalidDiagnostic(self):
        ''' Tests querying invalid MCB counters methods '''
        self.assertEqual(None, self.control.getDiagnostic(-1))
        self.assertEqual(None, self.control.getDiagnostic(17))
        self.assertEqual(None, self.control.getDiagnostic(None))
        self.assertEqual(None, self.control.getDiagnostic([1,2,3]))

    def testAddRemoveSingleClients(self):
        ''' Test adding and removing a host '''
        self.assertFalse(self.access.check("192.168.1.1"))
        self.access.add("192.168.1.1")
        self.assertTrue(self.access.check("192.168.1.1"))
        self.access.add("192.168.1.1")
        self.access.remove("192.168.1.1")
        self.assertFalse(self.access.check("192.168.1.1"))

    def testAddRemoveMultipleClients(self):
        ''' Test adding and removing a host '''
        list = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
        self.access.add(list)
        for host in list:
            self.assertTrue(self.access.check(host))
        self.access.remove(list)

#---------------------------------------------------------------------------#
# Main
#---------------------------------------------------------------------------#
if __name__ == "__main__":
    unittest.main()
