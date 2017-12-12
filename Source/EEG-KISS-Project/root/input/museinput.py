import logging
import sys
import serial
import struct 

from root.core.observerpattern  import Subject
from root.core.processingthread import ProcessingThread
from root.core.coretime         import CoreTime
from root.core.constants        import States, PatternStrings, Testing
from time import sleep

class MuseInput( Subject, ProcessingThread ):
    def __init__( self, blackboard, pattern  ):
        Subject.__init__( self )
        ProcessingThread.__init__( self )

        self.reset()

        self.blackboard = blackboard
        self._pattern   = pattern
        self._socket    = None
        self._battery   = -1

        self._serial_state  = States.IDLE
        self._port_state    = States.IDLE

        self.logger = logging.getLogger()        

    def reset(self):
        self._timestamp_offset  = 0
        self._timestamp         = 0
        self.last_time          = 0
        self.start_time         = 0
        self.total_time         = 0
        self._start             = 0
        self._rt_prev           = 0
        self._latest_timestamp  = 0

    def send_battery_command(self):
        # TODO: Convert list to string including hex values
        data = 'BAN\x09\x00gBattery\x00'
        return self._send(data)
    
    
    def start(self, name = 'no_name'):
        """
        Starts scanning for data unless thread is already running
        Continuously read bytes from port, parse the data and write to blackboard
        """
        result = False
        # TODO: check whether pattern and blackboard are set properly.
        if not self._running and self._socket != None:
            self.reset()
            self._first = True
            try:
                self._serial_state = States.BUSY
                
                if self.send_startup_command():
                    if self.send_run_command('On'):
                        self.byte_buffer = [ 0 for _ in range(3)]

                        for pattern in self.get_addresses():
                            self.blackboard.clear(pattern)

                        ProcessingThread.start(self, interval = 0.1, name = name)

                        self.notify_observers()

                        result = True

            except Exception as e:
                self.logger.log(logging.CRITICAL, (__file__, ": Exception during start: " , e ))
                self._port_state = States.IDLE
                self.stop()
            finally:
                self._port_state = States.IDLE
                return result

        return result


    def stop(self):
        """ 
        Stops scanning for data and closes serial port
        """
        if self._socket != None:
            self.send_run_command('Off')
            ProcessingThread.stop( self )
            self._port_state = States.IDLE
            self._serial_state = States.IDLE
    
    
    def set_connection(self, socket = None):
        """
        For proper working with this module, object 'socket' must contain methods:
            send(data)
            data = recv(size)
            close()
        """
        self._socket = socket
    
    
    def disconnect(self):
        if self._socket != None:
            if self._running:
                self.stop()
            self._socket.close()
            self._socket = None


    def is_connected(self):
        return self._socket != None
    
    
    def get_time(self):
        return self._latest_timestamp
    
    
    def get_duration(self):
        return self._latest_timestamp - self.start_time


    def is_streaming(self):
        return self._running
    
    
    def get_battery(self):
        return self._battery
    
    
    def get_serial_state(self):
        return self._serial_state
    
    
    def get_port_state(self):
        return self._port_state

    def is_idle(self):
        return ProcessingThread.isIdle(self) and self._port_state == States.IDLE and self._serial_state == States.IDLE



