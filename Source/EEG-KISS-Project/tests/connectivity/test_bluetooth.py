'''
Created on Oct 2, 2015

@author: Sjors.Ruijgrok
'''
from mock import patch

import unittest
#from root.connectivity.bluetooth_connection import Bluetooth

class BluetoothMock(object):
    
    class BluetoothSocket:
        def __init__(self):
            pass
    
    def discover_devices (self, duration=8, flush_cache=True, lookup_names=False,
                          lookup_class=False, device_id=-1):
        return [("F9:9C:56:78:F9:D6", "Wireless EEG")]
    
    def find_service (self, name = None, uuid = None, address = None):
        services = {'name'            : 'foo',
                    'host'            : 'foo',
                    'description'     : 'foo',
                    'provider'        : 'foo',
                    'protocol'        : 'foo',
                    'port'            : 'foo',
                    'service-classes' : 'foo',
                    'profiles'        : 'foo',
                    'service-id'      : 'foo'}
        
        return [services] 

class Test(unittest.TestCase):
    # Tests are disabled because the bluetooth library 
    # is not available on OSX (which is the OS of the buildserver)

    def setUp(self):
        #self.BluetoothObject = Bluetooth()
        self.BluetoothMock   = BluetoothMock()

    def tearDown(self):
        pass

    @patch('bluetooth.discover_devices')
    def _test_find_devices(self, bluetooth_mock):
        '''
        Test RFCOMM connection with EEG-headset.
        '''
        bluetooth_mock.return_value = self.BluetoothMock.discover_devices()
        
        bt_devices = self.BluetoothObject.findDevices(True)

        self.assertEquals(bt_devices, self.BluetoothMock.discover_devices())
        self.assertEquals(len(bt_devices), len(self.BluetoothMock.discover_devices()))
        
    @patch('bluetooth.find_service')
    def _test_find_services(self, bluetooth_mock):
        EEG_addr = []
        EEG_addr.append("F9:9C:56:78:F9:D6")
        
        bluetooth_mock.return_value = self.BluetoothMock.find_service()
        
        services = self.BluetoothObject.findServices(EEG_addr[0])
        
        self.assertEquals(services, self.BluetoothMock.find_service())
        self.assertEquals(len(services), len(self.BluetoothMock.find_service()))        
        # socket = self.BluetoothObject.connectClient_RFCOMM(services)
        
        # Startup command used to exit bootloader:
        #
        # Preamble       Length      Payload
        # 'B', 'A', 'N', 0x08, 0x00, "startup", 0x00
        
        #data = 'BAN\x08\x00startup\x00'
        
        #self.BluetoothObject.sendClient(socket, data)
        #sleep(1)
        
        # Command to start streaming of EEG-data:
        #
        # Preamble       Length      Payload
        #                            Command Setting, Option Key   Value
        # 'B', 'A', 'N', 0x08, 0x00, 's'     "Run",   0x00,  "On", 0x00
        
        #data = 'BAN\x08\x00sRun\x00On\x00'
        # self.BluetoothObject.sendClient(socket, data)
        
        # TODO: Check received data
        # data = self.BluetoothObject.receiveClient(socket, 2048)
        #print data
        
        #socket.close()

if __name__ == "__main__":
    unittest.main()
