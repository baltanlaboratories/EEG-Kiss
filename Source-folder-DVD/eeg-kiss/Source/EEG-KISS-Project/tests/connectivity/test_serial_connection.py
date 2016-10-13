import unittest
import serial
from mock import patch
from root.connectivity.serial_connection import SerialSocket 

class SerialMock(object):
    
    PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 'N', 'E', 'O', 'M', 'S'
    STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO = (1, 1.5, 2)
    FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = (5, 6, 7, 8)    
    
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
        pass

class TestSerialConnection( unittest.TestCase ):
    
    def test_init_none_port(self):
        """
        Tests for initialization with port of none-type
        """
        socket = SerialSocket()
        
    @patch('serial.Serial')
    def test_init_port(self, serial_mock):
        """
        Tests for initialization with port
        """
        serial_mock.return_value = SerialMock
        
        socket = SerialSocket(42)        
        
if __name__ == "__main__":
    unittest.main()