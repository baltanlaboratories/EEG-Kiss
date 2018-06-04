import logging, sys, serial, struct, OSC, threading, time, string, random

from root.core.observerpattern  import Subject
from root.core.processingthread import ProcessingThread
from root.core.constants        import States, PatternStrings

class MuseInput( Subject, ProcessingThread ):
    def __init__( self, headsetid, blackboard, pattern ):
        Subject.__init__( self )
        ProcessingThread.__init__( self )

        self.reset()

        self.blackboard = blackboard
        self._pattern   = pattern
        self._filter_on_headset = True
        self._subscribed = False
        
        self.logger = logging.getLogger()

        print ("muse input init id %i", headsetid)

    def reset(self):
        self._timestamp_offset  = 0
        self._timestamp         = 0
        self.last_time          = 0
        self.total_time         = 0
        self._start             = 0
        self._rt_prev           = 0
        self.start_time         = time.time()
        self._latest_timestamp  = self.start_time
        if hasattr(self, 'OSCserver') and self.OSCserver.running:
            self._running = True
            self._port_state = States.BUSY
            self._serial_state = States.BUSY
        else:
            self._running = False
            self._port_state = States.IDLE
            self._serial_state = States.IDLE
        print ('reset called')

    def parse_packet(self, channel, value, timestamp):
        pattern = self._pattern + PatternStrings.CHANNEL + str(channel)

        timestamp = timestamp - self.start_time
        self.blackboard.put_data(pattern, value, timestamp)
        #print ('pattern', pattern, 'sample_value', sample_value, 'timestamp', timestamp)

        
    def OSCserver_callback(self, path, tags, args, source):
        # tags will contain 'fff'
        # args is a OSCMessage with data
        # source is where the message came from (in case you need to reply)

        self._latest_timestamp = time.time()
        for i in range(len(args)):
#            print(i, args[i])
            self.parse_packet(i+1, args[i], self._latest_timestamp + (i / 256.0))

        self.notify_observers('update_time')

    def OSCserver_callback_on_forehead(self, path, tags, args, source):
        # tags will contain 'fff'
        # args is a OSCMessage with data
        # source is where the message came from (in case you need to reply)

        #print ('path:', path, 'tags:', tags, 'args:', args, 'source:', source)
        if self._filter_on_headset:
            self.subscribe_data(args[0] == 1)

    def start(self, headsetnum, name = 'no_name'):
        self.start_time         = time.time()
        self._port_state = States.BUSY
        self._serial_state = States.BUSY
        print ("museinput start")
        if not hasattr(self, 'OSCserver'):
            self.OSCserver = OSC.OSCServer( ("localhost", 7001 + headsetnum) );
            print ("museinput OSCServer initialized")
            self.OSCserver.addMsgHandler( "eegkiss/elements/touching_forehead", self.OSCserver_callback_on_forehead )
            self.set_filter_on_forehead(False)
            self.subscribe_data(True)
        
        self.OSCserver.running = True

        print "Registered Callback-functions:"
        for addr in self.OSCserver.getOSCAddressSpace():
            print addr

        ProcessingThread.start(self, 0.5, name)

        self.notify_observers()

        self._running = True

        return self._running

    def process_step(self):
        if self.OSCserver.running:
            self.OSCserver.handle_request()

    def stop(self):
        self.OSCserver.running = False
        ProcessingThread.stop( self )
        self.reset()
        
    def set_connection(self, socket = None):
        print ("set_connection called, _socket can be used")
        self._socket = socket
    
    def disconnect(self):
        self.stop()

    def is_connected(self):
        return True
    
    def get_time(self):
        return self._latest_timestamp - self.start_time
    
    def get_duration(self):
        #print ('get_duration', self._latest_timestamp - self.start_time)
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
        isidleval = ProcessingThread.isIdle(self) and self._port_state == States.IDLE and self._serial_state == States.IDLE
        #print ('isidle', isidleval)
        return isidleval

    def send_battery_command(self):
        pass

    def set_filter_on_forehead(self, enabled):
        """
        With the filter enabled, data is only send if the headband has contact with the skin.
        """
        self._filter_on_forehead = enabled

    def subscribe_data(self, enabled):
        if self._subscribed == enabled:
            return
        addresses = ["eegkiss/eeg", "eegkiss/eeg/quantization","eegkiss/eeg/0", "eegkiss/notch_filtered_eeg"]
        if (enabled):
            for address in addresses:
                self.OSCserver.addMsgHandler( address, self.OSCserver_callback ) 
        else:
            for address in addresses:
                self.OSCserver.delMsgHandler( address)
        self._subscribed = enabled
