import logging
import sys
import serial
import struct 

from root.core.observerpattern  import Subject
from root.core.processingthread import ProcessingThread
from root.core.coretime         import CoreTime
from root.core.constants        import States, PatternStrings, Testing
from time import sleep

def chunks( data, l ):
    """ 
    Chops up a list into a list of lists of size l
    Does not check whether the last list has the correct size
    """
    return [ data[i*l:(i+1)*l] for i in range( len(data) / l ) ]

def little_endian( byte0, byte1 ):
    """ 
    Calculates little endian unsigned integer from two bytes
    """
    return  byte0 + byte1 * 256

class ImecInput( Subject, ProcessingThread ):
    """
    Reads data from a serial port, parses it as Imec headset data and stores the data in blackboard buffers
    For parsing details, look at the Imec document
    """
    
    def __init__( self, blackboard, pattern ):
        """
        Parameters
        ==========
        @param blackboard:        
            Blackboard instance to buffer incoming data
        @param pattern:
            The pattern for this headset under which it is buffered on the blackboard 
        """
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
    
    
    def _parse_impedance_packet(self, pack, timestamp=None ):
        """ 
        Eight packets of two bytes
        First byte is ImpI, second is ImpQ
        """
        # TODO: Verify output with Imec application. Should possibly do 'byte % 16' as values are only four bits
        sample_data = chunks( pack, 2)
        for sample in sample_data:
            sample_values   = bytearray( sample ) 
            
            pattern         = self._pattern + PatternStrings.SIGNAL_IMPI
            self.blackboard.put_data(pattern, sample_values[0], timestamp )
            pattern         = self._pattern + PatternStrings.SIGNAL_IMPQ
            self.blackboard.put_data(pattern, sample_values[1], timestamp )
    
    
    def _parse_eeg_packet(self, eeg_pack, timestamp ):
        """  
        Every EEG block contains 8 pairs of two bytes
        Value is stored as 12-bit unsigned integer in 16-bit word
        """ 
        sample_data         = chunks( eeg_pack, 2)
        for index, sample in enumerate( sample_data ):
            pattern         = self._pattern + PatternStrings.CHANNEL + str(index + 1)
#             sample_bytes    = bytearray(sample)
#             sample_value    = little_endian( sample_bytes[0], sample_bytes[1] % 16 )
            sample_value = self._bytesToInt12(sample)
            
            #print sample_value, timestamp
            self.blackboard.put_data(pattern, sample_value, timestamp)
            
            self._latest_timestamp = timestamp
    
    
    def _parse_dc_offset(self, data):
        """
        You need DC Offset data? Implement this...
        Parse the data and send it to the blackboard
        """
        pass
    
    
    def _parse_accelerometer(self, data):
        """
        You need accelerometer data? Implement this...
        Parse the data and send it to the blackboard
        """
        pass
    
    
    def _parse_eeg_data(self, data, timestamp):
        """
        EEG data is parsed and written to a buffer on the blackboard
        Every EEG data packet contains four EEG block and one IMP block
        Every block contains 16 bytes: 8 channels of 2 bytes
        Every pair of EEG bytes is a little-endian representation of the sample data
        """
        #print 'Data-length: ', len(data), 'Timestamp: ', timestamp
        try:
            if len( data ) == 320:
                if self._first:
# NOTE: Waiting for first timestamp with value 4096 is necessary for the headset, because the first packets (with len 320) have higher timestamps,
#       and these packets don't seem to be EEG-packets.
#       When testing with simulator and simulator is already running, timestamp 4096 will not come anymore.
                    if not Testing.SERIAL_SIMULATOR:
                        if timestamp != 4096:
                            return
                    self._timestamp_offset = timestamp
                
                if not self._first:
                    if timestamp < self._timestamp:
                        self.logger.log(logging.CRITICAL, (__file__, ": Timestamp mismatch: new timestamp ", timestamp, " < previous ", self._timestamp))       
                    elif (timestamp - self._timestamp) != 4096:
                        self.logger.log(logging.CRITICAL, (__file__, ": Timestamp mismatch: missed ", (timestamp - self._timestamp)/4096, " EEG-packets (", (timestamp - self._timestamp)/256, " samples)" )) 
                
                self._timestamp      = timestamp
                calibrated_timestamp = timestamp - self._timestamp_offset
                
                dif = (calibrated_timestamp - self.last_time) / (256.0 * 256.0)
                
                new_total_time = dif + self.total_time
                self.total_time = new_total_time
                if self._first:
                    self.start_time = self.total_time
                    self._first     = False
                    # NOTE: Next is debug-code to show time-drifting between writing to COM-port (headset) and reading from COM-port.
                    #       With thread-interval set to 0.1 ms headset reading seems to go well, but hs-simulator seems to write too fast.
#                     self._start = CoreTime().now()
#                     self._rt_prev = 0
#                 rt = CoreTime().now() - self._start
#                 rt_dif = rt - self._rt_prev
#                 self._rt_prev = rt
#                 ts = self.total_time - self.start_time
#                 print dif, rt_dif, timestamp, rt, ts, (rt - ts)#, ts_data[3].encode('hex'), ts_data[2].encode('hex'), ts_data[1].encode('hex'), ts_data[0].encode('hex')
                
                self.last_time = calibrated_timestamp
                
                # a complete data block contains 80 bytes, there are four in total
                blocks = chunks( data, 80 ) 
                for block_index,block in enumerate(blocks):
                    # Every block contains 5 packets of 16 bytes
                    # Every second block is the impedence block
                    # The other four blocks contain EEG data
                    packets         = chunks( block, 16)
                    eeg_packets     = [packets[0]] + packets[2:]
#                     imp_packet      = packets[1]
                    
                    for index, eeg_pack in enumerate(eeg_packets):
                        self._parse_eeg_packet( eeg_pack, new_total_time + (block_index*4.0 + index) / 256.0 )
                    # TODO: Enable this with some flag.
#                     self._parse_impedance_packet( imp_packet, new_total_time )
    
                self.notify_observers('update_time')
                
            elif len( data ) == 324:
                self._parse_dc_offset( data )
            elif len( data ) == 192:
                self._parse_accelerometer( data )
        
        except Exception as e:
            self.logger.log(logging.CRITICAL, (__file__, ": _parse_eeg_data() -> ", e )) 
            raise e
    
    
    def _bytesToInt12(self, data):
        return ord(data[0]) + (ord(data[1]) % 16)*0x0100
    
    
    def _bytesToInt32(self, data):
        return ord(data[0]) + ord(data[1])*0x0100 + ord(data[2])*0x010000 + ord(data[3])*0x01000000
    
    
    def _parse_data(self, payload_data ):
        """
        Parse the data of a data package (where command is 'd')
        Correct parsing algorithm is called corresponding to the ID value.
        Currently, only ID 0 is send by the headset.
        """
#         new_ts = struct.unpack("<L", payload_data[:4])[0]
        new_ts      = self._bytesToInt32(payload_data)
        payload_id  = ord(payload_data[4])
        data        = payload_data[5:]
        
        #ts_data = payload_data[:4]
        
        if payload_id == 0 and new_ts > 0:  # TODO: Check why first timestamp should not be zero.
            self._parse_eeg_data( data, new_ts )
            #self._parse_eeg_data( data, new_ts, ts_data )
        else:
            if payload_id != 0:
                raise NotImplementedError('ID \'%d\' not implemented!' % (payload_id))

    
    def _parse_setting( self, payload_data ):
        """
        All Responses from headset are currently printed
        Some ofthis information could be parsed to be presented in a GUI
        """
        # print ''.join(payload_data)
        if ''.join(payload_data).startswith('Battery'):
            try:
                bat = ''.join(str(s) for s in payload_data[8:] if s.isdigit())
                self._battery = int(bat)
                self.notify_observers('battery')
            except Exception as e: 
                self.logger.log(logging.CRITICAL, (__file__, ": _parse_setting(\'Battery\') -> ", e ))     
    

    def _parse_remarks( self, payload_data ):
        print str(payload_data)
    
    
    def _parse_set( self, payload_data ):
        # print str(payload_data)
        pass
    
    
    def _parse_enumerate( self, payload_data ):
        print str(payload_data)
    
    
    def _parse_payload( self, payload_data ):
        """
        Parse the payload of a data package. 
        Correct parsing algorithm is called based on command value
        """
        command = payload_data[0]
        data    = payload_data[1:]
        
        if command == 'd':
            self._parse_data( data )
        elif command == 'g':
            self._parse_setting( data )
        elif command == 'r':
            self._parse_remarks( data )
        elif command == 's':
            self._parse_set( data )
        elif command == 'e':
            self._parse_enumerate( data )
        elif command == 'b':
            self.send_startup_command()
        else:
            raise NotImplementedError('command \'%s\' not implemented!' % (command))
    
    
    def process_step(self):
        """
        This method must be implemented in a subclass and should implement a repetitive task
        """
        if self._socket != None:
            # read new byte
            self._port_state = States.BUSY

            try:
                new_element = self._receive(1)
                
                # push byte in buffer
                self.byte_buffer = (self.byte_buffer + new_element)[-3:]
    
                # check for Preamble
                if self.byte_buffer == ['B', 'A', 'N']:
                    # Read length of payload
                    length_bytes = self._receive(2)
                    payload_length = little_endian(ord(length_bytes[0]), ord(length_bytes[1]))
                    # Read payload
                    payload = self._receive(payload_length)
                    # Parse payload
                    self._parse_payload(payload)
                    
            except Exception as e:
                self.stop()
                self.logger.log(logging.CRITICAL, (__file__, ": Exception during receive: ", e )) 
            finally:
                self._port_state = States.IDLE
    
    
    def _send(self, data):
        result = False
        if self._socket != None and len(data) > 0:
            # print data
            try:
                self._socket.send(data)
                result = True
            except Exception as e:
                self.logger.log(logging.CRITICAL, (__file__, ": Exception during send: ", e )) 

        return result
    
    
    def _receive(self, size = 1):
        data = []
        if self._socket != None and size > 0:
            # TODO: Implement timeout
            try:
                for _ in xrange(size):
                    # TODO: Get all data at once and parse as string i.s.o. list
                    new_data = self._socket.recv(1)
                    if new_data != None:  # TODO?: Or should we check len(new_data) == 1?
                        data.append(new_data)
                        # print new_data.encode('hex'), '-', new_data
                    else:
                        self.logger.log(logging.CRITICAL, (__file__, ": No data available")) 
                if len(data) != size:
                    self.logger.log(logging.CRITICAL, (__file__, ": Data-size mismatch (requested: ", size, ", received: " , len(data),")"  ))
            except Exception as e:
                self.logger.log(logging.CRITICAL, (__file__, ": Socket is none or size is less than 0 -> ", e ))
                raise e
        
        return data
    
    
    def _send_command(self, command, setting):
        """
        Send a command to the headset. See protocol document for details.
        @param command:
            one-character command identifier
        @param setting:
            Setting/key value of command
        """
        setting = list( setting )
        data    = ['B', 'A', 'N']
        length  = [len( setting ) + 2, 0]
        data    = data + length + [command] + setting + [0]
        
        print data
#         self._send(data)
    
    
    def send_get_command(self, setting):
        if self._socket == None:
            return False
        
        try:
            self._send_command('g', setting)
            return True
        except Exception as e:
            self.logger.log(logging.CRITICAL, (__file__, ": get: ", setting, ", -> " , e ))
            self._port_state = States.IDLE
            self.stop()
            return False
    
    
    def send_enumerate_command(self, setting=''):
        self._send_command( 'e', setting )
    
    
    def send_set_command(self, setting, value):
        command = list( setting ) + [0] + list( value )
        self._send_command( 's', command )
    
    
    def send_startup_command(self):
        # TODO: Convert list to string including hex values
#         data    = ['B', 'A', 'N']
#         length  = [8, 0]
#         data    = data + length + list( 'startup' ) + [0]
#         self._send(data)
        data = 'BAN\x08\x00startup\x00'
        
        return self._send(data)
    
    
    def send_run_command(self, value):
        # TODO: Convert list to string including hex values
        if value == 'On':
            data = 'BAN\x08\x00sRun\x00On\x00'
        else:
            data = 'BAN\x09\x00sRun\x00Off\x00'
        
        return self._send(data)
    
    
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
    
    
    def get_addresses(self):
        """ 
        Returns list of all blackboard buffers which are supplied with data by this headset 
        """
        pats = [ PatternStrings.CHANNEL + '%d' % (i) for i in range(1,9) ] + [ PatternStrings.SIGNAL_IMPI, PatternStrings.SIGNAL_IMPQ ]
        return [ self._pattern + pat for pat in pats ]
    
    
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
