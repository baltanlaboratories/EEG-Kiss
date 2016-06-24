import sys
import struct
import threading
import socket

import serial

from audioop        import reverse

from root.input.imecinput import ImecInput

class UDPImecInput( ImecInput ):
    """
    DOES NOT WORK PROPERLY!
    THE DATA AS FORWARDED BY THE IMEC GUI IS NOT THE SAME AS RECEIVED BY THE HEADSET!
    
    THIS CLASS IS MEANT TO PROCESS THE DATA AS FORWARDED BY THE IMEC GUI OVER UDP!
    """
    
    def __init__( self, port, blackboard, patterns ):
        self._port = port
        self.blackboard = blackboard
        self._patterns = patterns
        
        self._socket = None
     
    def _start_receiving_data(self):
        """ Continuously read bytes from port, parse the data and write to blackboard
        """
        
        # init byte buffer of length 3, length of preamble
        buffer = [ 0 for _ in range(3)]
        
        self._running = True
        while self._running:
            # read new byte
            buffer     = self._socket.recvfrom(1024)
            
            print len([ord(i) for i in buffer[0] ])
            
            # check for Preamble
            if buffer == ['B', 'A', 'N']:
                # Read length of payload
                length_bytes    = self._socket.recvfrom(2)
                payload_length  = little_endian( [ord(length_bytes[0]), ord(length_bytes[1])] )
                if payload_length == 326:
                    # Read payload
                    payload = self._socket.recvfrom( payload_length )
                    
                    # Parse payload
                    self._parse_payload( payload )
    
    def start(self):
        # TODO: check whether patterns and blackboard are set properly.
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(("127.0.0.1", self._port))
        
        threading.Thread( target=self._start_receiving_data ).start()
        
        
    def stop(self):
        if self._socket:
            self._running = False
            self._socket.close()
    