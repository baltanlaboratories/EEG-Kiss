'''
Created on 13 mei 2015

@author: Bas.Kooiker
'''
import logging

from root.input.datasimulator   import DataSimulator
from root.core.coretime         import CoreTime
from root.core.observerpattern  import Subject
from root.core.processingthread import ProcessingThread

class TimedSimulator( DataSimulator ):

    def __init__(self, arg0, marker_pattern=None ):
        
        self._counters  = []
        self._done      = []
        self._marker_pattern = marker_pattern
        self._current_time   = 0
        self.logger          = logging.getLogger()
        
        if isinstance(arg0, DataSimulator):
            DataSimulator.__init__( self, arg0.blackboard )
            self._observers = arg0._observers
        else:
            DataSimulator.__init__( self, arg0 )
            Subject.__init__( self )
    
    def process_step(self):
        """
        Inherited from ProcessingThread
        """
        if self._state is self.PLAYING:
            now = CoreTime().now() + self._offset    
            # Send all data samples which should be sent since start of playback
            if self._state != self.PLAYING:
                return
            
            self._current_time = now
            
            if self._first:
                #print 'Playback started at:', now
                #for index, pattern in enumerate( self._patterns ):
                #    print 'count[%s] = %d' % (pattern, self._counters[index])
                self._first = False
            
            for index, pattern in enumerate( self._patterns ):
                while True:
                    counter     = self._counters[index]
                    stamplist   = self._timestamps[index]
                    
                    if counter >= len( stamplist ):
                        #print "Done:", index, "Pattern:", pattern
                        self._done[index] = True
                        break
                    
                    timestamp   = stamplist[counter]
                    
                    if timestamp > now:
                        #print self._counters[index], timestamp, len(stamplist)
                        break
                    
                    value       = self._samples[index][counter]
    
                    #print now, pattern, value, timestamp, self._offset
                    self.blackboard.put_data( pattern, value, timestamp )
                    self._counters[index] += 1
        
            if all( self._done ):
                self.stop()
                self.notify_observers('stop_playback')
                return
    
            self.notify_observers('update_time')
    
    ### Setters ###
    def set_simulation_data(self, data):
        """
        @param data:
        """    
        self._samples       = [ [ v[0] for v in channel ] for channel in data ]
        self._timestamps    = [ [ v[1] for v in channel ] for channel in data ]   
        self.reset()
    
    def get_current_time(self):
        """
        Returns the current playback time
        """
        if not self.is_data_set():
            return -1
        return self._current_time   
    
    def reset(self):
        self._done          = [ False for _ in range( len(self._samples) )]
        self._counters      = [ 0 for _ in range( len(self._samples) )]
        self._offset        = 0
        self._first         = True
        
        for pattern in self._patterns:
            self.blackboard.clear(pattern)
    
    def get_total_time(self):
        if not self.is_data_set():
            return -1
        return max( [ chan[-1] for chan in self._timestamps ] )
    
    def set_time(self, set_time):
        """
        Sets the current playback time in seconds
        """
        if not self.is_data_set():
            return 
        
        self.logger.log(logging.INFO, (__file__, ": Time was set. Time = ", set_time))
        print 'set_time:', set_time
 
        self.reset()
        self._offset = set_time
        for index, _ in enumerate( self._patterns ):
            while True:
                try:
                    counter     = self._counters[index]
                    stamplist   = self._timestamps[index]
                    timestamp   = stamplist[counter]
                    t = round(timestamp)
                    #print t, set_time, index, counter, self._counters[index], len(stamplist)
                    if t >= set_time or (counter + 1) >= len(stamplist):
                        break
                    self._counters[index] += 1
                except Exception as e:
                    print 'Exception set_time:', e
                    break
    
    def start( self, name = 'no_name' ):
        """
        Wraps ProcessingThread
        Simulate data on a separate thread
        If paused, resume playback
        If already playing, do nothing
        """
        if not self.is_data_set():
            return
        
        #print 'Start simulator:', name
        ProcessingThread.start( self, name = name )
        self._state = self.PLAYING
    
    def pause(self):
        """
        Pauses simulation of data
        """
        if not self._state is self.IDLE:
            self._state     = self.PAUSED
            self._offset    = self._current_time
