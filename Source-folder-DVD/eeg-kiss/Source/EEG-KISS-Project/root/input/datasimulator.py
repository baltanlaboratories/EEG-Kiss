# import time
import threading
from root.core.coretime import CoreTime
from root.core.observerpattern import Subject
from root.core.processingthread import ProcessingThread
from root.core.constants import BufferTypes

class DataSimulator( ProcessingThread, Subject ):
    """
    This DataSimulator simulates data from a recorded data file and presents the data on a Blackboard instance.
    There are three states for the simulator: Idle, Paused and Playing. When paused, the simulator will remain active
    but will wait with presenting the simulated data until resumed. 
    """
    
    # Some constants
    IDLE    = 1
    PAUSED  = 2
    PLAYING = 3
    
    def __init__( self, arg0 ):
        """
        @param blackboard:
            The blackboard on which the simulated data will be presented
        """
        ProcessingThread.__init__( self )
        Subject.__init__( self )
        self.clear_data()
        
        if isinstance(arg0, DataSimulator):
            self.blackboard = arg0.blackboard
            self._observers = arg0._observers
            return
        
        self.blackboard = arg0
        
    def clear_data(self):
        """
        Resets all state variables 
        """
        self._patterns          = []
        self._samples           = None
        self._interval          = 0
        self._state             = self.IDLE
        self._sample_number     = 0
        self._counters          = []
        self._index_offset      = 0
        self._start_time        = CoreTime().now()
        
    ### Setters ###
    def set_simulation_data(self, data):
        """
        @param data:
            set data streams for simulation. Should be two-dimensional list
            should be the same number of columns as patterns
        """      
        self._samples = data
        
    def set_simulation_interval(self, interval):
        """
        @param interval:
            set sample interval for simulation
        """
        self._interval = interval

    def set_patterns(self, patterns):
        """ 
        @param patterns: 
            for distinguishing between multiple headsets
        """
        self._patterns = patterns
         
    ### Methods ###   
    def start( self, name = 'no_name' ):
        """
        Wraps ProcessingThread
        Simulate data on a separate thread
        If paused, resume playback
        If already playing, do nothing
        """
        if not self.is_data_set():
            return
          
        if self._state is self.IDLE:
            self._start = CoreTime().now()
            ProcessingThread.start( self, name=name )
            self.reset()
        elif self._state is self.PAUSED:
            self._start = CoreTime().now()
        self._state = self.PLAYING
             
    def reset(self):
        self._index_offset  = 0
        self._sample_number = 0
             
    def pause(self):
        """
        Pauses simulation of data
        """
        if not self._state is self.IDLE:
            self._state         = self.PAUSED
            self._index_offset  = self._sample_number
               
    def stop( self ):
        """
        Stop simulation of data 
        """
        #print 'Stop simulator:', self.getName()
        ProcessingThread.stop(self)
        self._state = self.IDLE
    
    ### Getters ###
    def is_data_set(self):
        """
        Checks whether the data variables are set correctly
        NOTE: Uncomment the 'print' lines if necessary during debugging.
        """
        if not self._samples:
            #print "Data not set"
            return False
        if not self.blackboard:
            #print "Blackboard was not set"
            return False
        if not len(self._patterns) == len(self._samples):
            #print "Number of data streams and number of patterns do not match"
            return False
        if self._interval <= 0:
            #print "Interval should be a strictly positive value"
            return False
        
        return True   
          
    def get_simulation_state(self):
        """
        Returns simulation state {PLAYING, IDLE, PAUSED}
        """
        return self._state

    def process_step(self):
        """
        Inherited from ProcessingThread
        """
        now = CoreTime().now()         
        # Send all data samples which should be sent since start of playback
        if self._state != self.PLAYING:
            return
        
        while True:
            sample_time = self._interval * self._sample_number 
            time_offset = self._interval * self._index_offset
            if ( self._start + sample_time - time_offset) > now:
                break
            
            if self._sample_number >= len( self._samples[0] ):
                self.notify_observers('stop_playback')
                self.stop()
                return
                       
            # Send data for the selected eeg channels
            for index, pattern in enumerate( self._patterns ): 
                try:
                    buffer = self._samples[index]
                    value = buffer[self._sample_number]
                    self.blackboard.put_data( pattern, value, sample_time )
                except IndexError as e:
                    self.notify_observers('stop_playback')
                    self.stop()
                    return
 
            self._sample_number += 1

    def get_total_time(self):
        """
        Returns total playback time in seconds
        """
        if not self.is_data_set():
            return -1
        return self._interval * len( self._samples[0] )
        
    def get_current_time(self):
        """
        Returns the current playback time based on the current sample number and interval
        """
        if not self.is_data_set():
            return -1
        return self._interval * self._sample_number
    
    def set_time(self, set_time):
        """
        Sets the current playback time in seconds
        """
        if not self.is_data_set():
            return 
        
        self._start_time        = CoreTime().now()
        self._index_offset      = int( set_time / self._interval )
        self._sample_number     = self._index_offset
    
    def set_state(self, state):
        self._state = state
