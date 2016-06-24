import serial
import sys
import unittest

from headset_simulator.serial_simulator     import SerialSimulator
from mock                                   import patch
from root.core.blackboard                   import Blackboard
from root.connectivity.serial_connection    import SerialSocket
from root.core.constants                    import Testing
from root.input.imecinput                   import ImecInput
from time                                   import sleep

class SerialMock(object):
    
    PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 'N', 'E', 'O', 'M', 'S'
    STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO             = (1, 1.5, 2)
    FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS                         = (5, 6, 7, 8)    
    
    BYTESIZES = (FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS)
    PARITIES  = (PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE)
    STOPBITS  = (STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO)    
    
    _port = None
    
    def __init__(self,
                 port = None,           # number of device, numbering starts at
                                        # zero. if everything fails, the user
                                        # can specify a device string, note
                                        # that this isn't portable anymore
                                        # port will be opened if one is specified
                 baudrate=9600,         # baud rate
                 bytesize=EIGHTBITS,    # number of data bits
                 parity=PARITY_NONE,    # enable parity checking
                 stopbits=STOPBITS_ONE, # number of stop bits
                 timeout=None,          # set a timeout value, None to wait forever
                 xonxoff=False,         # enable software flow control
                 rtscts=False,          # enable RTS/CTS flow control
                 writeTimeout=None,     # set a timeout for writes
                 dsrdtr=False,          # None: use rtscts setting, dsrdtr override if True or False
                 interCharTimeout=None  # Inter-character timeout, None to disable
                 ):
        self._isOpen    = True
        self._baudrate  = 0

    def close(self):
        self._isOpen = False
    
    def write(self, data_packet):
        pass

    def flush(self):
        pass

    def isOpen(self):
        return self._isOpen

    def setBaudrate(self, baudrate):
        self._baudrate = baudrate

    def getBaudrate(self):
        return self._baudrate

class TestImecInput(unittest.TestCase):

    def startUp(self):
        '''
        Helper-method for starting up headset-simulator, opening COM-port and set connection
        '''
        # Start headset-simulator
        self.hs_simulator = SerialSimulator()
        self.hs_simulator.start()

        # Get socket for serial connection
        self._socket = SerialSocket(Testing.SERIAL_PORT)

        # And pass this socket to imec
        self.imec.set_connection(self._socket)
    
    def setUp(self):
        self.test_pattern = 'test_eeg'
        self.test_buffer  = Blackboard()
        self.imec         = ImecInput(self.test_buffer, self.test_pattern)

    def tearDown(self):
        self.test_buffer.clear(self.test_pattern)

#     @unittest.skip('skip test_01')
    def test_01_init(self):
        """
        Test initalization of ImecInput
        """
        self.assertEqual(self.imec.blackboard, self.test_buffer, "Blackboard not set")
        self.assertEqual(self.imec._pattern, self.test_pattern, "Incorrect pattern")
        self.assertTrue(self.imec._socket == None, "Socket should not be set")

        self.assertFalse(self.imec.start('hs1'), "Start streaming should fail")
        self.assertFalse(self.imec.is_streaming(), "Should not be streaming")
        self.assertFalse(self.imec.is_connected(), "Should be disconnected")

    @patch('serial.Serial')
    def test_02_startStreaming(self, serial_mock):
        """
        Test start/stop streaming with/without connection 
        """
        self.startUp()

        serial_mock.return_value = SerialMock

        self.assertTrue(self.imec.is_connected(), "Should be connected")
        self.assertFalse(self.imec.is_streaming(), "Should not be streaming yet")

        # Start streaming
        self.assertTrue(self.imec.start('hs1'), "Start streaming failed")
        self.assertTrue(self.imec.is_streaming(), "Should be streaming")

        sleep(0.2)

        self.assertFalse(self.imec.start('hs2'), "Start during streaming should fail")

        self.imec.stop()
        # Wait for thread has stopped
        while not self.imec.is_idle():
            pass

        self.hs_simulator.stop()

        self.assertFalse(self.imec.is_streaming(), "Still streaming after stop")
        self.assertTrue(self.imec.is_connected(), "Should still be connected")

        self.imec.disconnect()
        self.assertFalse(self.imec.is_connected(), "Should be disconnected")

    @patch('serial.Serial')
    def test_03_restartAfterStop(self, serial_mock):
        self.startUp()

        serial_mock.return_value = SerialMock

        self.assertTrue(self.imec.is_connected(), "Should be connected")

        self.assertTrue(self.imec.start('hs1'), "Start streaming failed")
        self.assertTrue(self.imec.is_streaming(), "Should be streaming")

        sleep(.2)

        # Stop streaming
        self.imec.stop()

        # Wait for thread has stopped
        while not self.imec.is_idle():
            pass

        self.assertFalse(self.imec.is_streaming(), "Still streaming after stop")
        self.assertTrue(self.imec.is_connected(), "Should still be connected")

        # Restart streaming
        self.assertTrue(self.imec.start('hs2'), "Restart streaming failed")
        self.assertTrue(self.imec.is_streaming(), "Not streaming after restart")

        sleep(.2)

        self.imec.stop()

        # Wait for thread has stopped
        while not self.imec.is_idle():
            pass

        self.hs_simulator.stop()

        self.assertFalse(self.imec.is_streaming(), "Still streaming after stop")
        self.assertTrue(self.imec.is_connected(), "Should still be connected")

        self.imec.disconnect()
        self.assertFalse(self.imec.is_connected(), "Should be disconnected")

    @patch('serial.Serial')
    def test_04_disconnectDuringStreaming(self, serial_mock):
        self.startUp()

        serial_mock.return_value = SerialMock

        self.assertTrue(self.imec.is_connected(), "Should be connected")

        self.assertTrue(self.imec.start('hs1'), "Start streaming failed")
        self.assertTrue(self.imec.is_streaming(), "Should be streaming")

        sleep(.2)

        # Disconnect during streaming -> streaming should stop
        self.imec.disconnect()

        # Wait for thread has stopped
        while not self.imec.is_idle():
            pass

        self.assertFalse(self.imec.is_connected(), "Should be disconnected")
        self.assertFalse(self.imec.is_streaming(), "Still streaming after disconnect during streaming")
        self.assertFalse(self.imec.start('hs2'), "Start streaming should fail after disconnect")

        # Reconnect
        self.imec.set_connection(self._socket)
        self.assertTrue(self.imec.is_connected(), "Should be connected")
        self.assertFalse(self.imec.is_streaming(), "Should not be streaming yet")

        self.assertTrue(self.imec.start('hs3'), "Start streaming after reconnect failed")
        self.assertTrue(self.imec.is_streaming(), "Should be streaming")

        sleep(.2)

        self.imec.stop()

        # Wait for thread has stopped
        while not self.imec.is_idle():
            pass

        self.hs_simulator.stop()

        self.assertFalse(self.imec.is_streaming(), "Still streaming after stop")
        self.assertTrue(self.imec.is_connected(), "Should still be connected")

        self.imec.disconnect()
        self.assertFalse(self.imec.is_connected(), "Should be disconnected")

    @patch('serial.Serial')
    def test_05_parseEEG(self, serial_mock):
        """
        Test parsing EEG-data
        """
        self.startUp()

        serial_mock.return_value = SerialMock

        self.assertTrue(self.imec.is_connected(), "Should be connected")
        self.assertFalse(self.imec.is_streaming(), "Should not be streaming yet")

        # Start streaming
        self.assertTrue(self.imec.start('hs1'), "Start streaming failed")
        self.assertTrue(self.imec.is_streaming(), "Should be streaming")

        sleep(.2)

        self.imec.stop()

        # Wait for thread has stopped
        while not self.imec.is_idle():
            pass

        self.hs_simulator.stop()

        self.assertFalse(self.imec.is_streaming(), "Still streaming after stop")
        self.assertTrue(self.imec.is_connected(), "Should still be connected")

        self.imec.disconnect()
        self.assertFalse(self.imec.is_connected(), "Should be disconnected")

        #for ch in range(4):
        #    count = self.test_buffer.get_count(self.test_pattern + '/channel_%d' % (ch + 1))
        #    #self.assertGreater(count, 0)

        #    data = self.test_buffer.get_data(self.test_pattern + '/channel_%d' % (ch + 1), count)
        #    self.assertEqual(len(data['data']), count, "Sample-count doesn't match")
        #    self.assertEqual(len(data['timestamps']), count, "Timestamp-count doesn't match")

        #    #print 'Received %d samples on channel %d' % (count, (ch + 1))
            
        #    for sample, timestamp in zip(data[0], data[1]):
        #        self.assertEqual(timestamp % 0.00390625, 0.0, "Timestamp failure")
        #        self.assertGreaterEqual(sample, 0, "Sample-value too low")
        #        self.assertLessEqual(sample, 4000, "Sample-value too high")

    def test_get_battery(self):
        self.assertEqual(self.imec.get_battery(), -1)

    def test_get_duration(self):
        self.assertEqual(self.imec.get_duration(), 0)

    def test_get_serial_state(self):
        self.assertEqual(self.imec.get_serial_state(), 0)

    def test_get_port_state(self):
        self.assertEqual(self.imec.get_port_state(), 0)

    def test_get_time(self):
        self.assertEqual(self.imec.get_time(), 0)

if __name__ == '__main__':
    unittest.main()
