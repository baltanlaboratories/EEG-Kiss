import numpy
import logging
import threading
from _collections import defaultdict

class BlackboardBuffer:
    """ 
    The buffer that blackboard uses for each pattern.
    The bufferlength specifies the maximum size of the buffer
    The buffer is a list of float values
    Count tracks the total number of processed samples
    """
    
    def __init__(self, pattern):
        """
        @param pattern:
            The pattern for which this buffer holds the data 
        """
        self._data         = []
        self._timestamps   = [] 
        self._size         = 512
        self._count        = 0
        self._pattern      = pattern
        
        self.logger = logging.getLogger()

        self._lock = threading.Lock()
    
    ### METHODS ###
    def put_data(self, value, timestamp=None):
        """
        adds data to this data buffer and increments the sample counter accordingly
        @param value:
            a single sample value or a list of sample values  
        """
        if not isinstance( value, numpy.ndarray ):
            if not isinstance(value, list):
                value = [value]
        
        with self._lock:
            for v in value:
                self._data.append( v )
                self._timestamps.append( timestamp )
                
                self._data = self._data[ -self._size : ]
                self._timestamps = self._timestamps[ -self._size : ]
                
                self._count += 1
    
    def get_data(self, count = None):
        """ If count != 0 then this requested count is ignored, all data will be returned """ 
        
        #=!=!=!=!=!=!=!=!=!=!=!=!=!=! NOTE !=!=!=!=!=!=!=!=!=!=!=!=!=!=
        # If performance is an issue, declare the dict one in __init__ 
        # to prevent rebuilding the dictionary every call        
                      
        if count == None:
            count = self._size

        if count == 0:
            return defaultdict(list, data=[], timestamps=[])

        with self._lock:
            data = self._get_data_values(count)
            timestamps = self._get_timestamp_values(count)
        
        return defaultdict(list, data=data, timestamps=timestamps)
        
        #return data, timestamps
    
    def _get_data_values(self, count):
        """ Returns the data from this buffer """
        return self._data[-count:]
    
    def get_data_window(self, first, last):
        if not len(self._data) > 0:
            return []
        
        if not first == None:
            index_first = self._timestamps.index(first)
        else:
            index_first = 0
            
        index_last = self._timestamps.index(last)
        
        return self._data[index_first:index_last]
    
    def _get_timestamp_values(self, count):
        """ Returns the data from this buffer """
        return self._timestamps[-count:]
    
    def get_timestamps_window(self, first, last):
        if not len(self._timestamps) > 0:
            return []
        
        if not first == None:
            index_first = self._timestamps.index(first)
        else:
            index_first = 0
            
        index_last = self._timestamps.index(last)
        
        return self._timestamps[index_first:index_last]
    
    def clear(self):
        """ remove all collected data """
        with self._lock:
            self._data = []
            self._timestamps = [] 
            self._count = 0
    
    ### SETTERS ###
    def set_bufsize(self, size ):
        """
        @param bufferlength 
            Sets the specified buffer length
        """
        self._size = size
    
    ### GETTERS ###
    def get_bufsize(self):
        """ Returns the current buffer length """
        return self._size
    
    def get_count(self):
        """ Returns the sample counter of this data buffer """
        
        if self._count >= self._size:
            ''' More data than the size of the buffer, data loss! '''
            self.logger.log(logging.CRITICAL, (__file__, ": The buffersize is ", self._size, " but there were ", self._count, " samples added. So there probably is data lost."))        
        
        return self._count
    
    def get_pattern(self):
        """ returns the pattern of this data buffer """
        return self._pattern
    
    def get_last_timestamp(self):
        """ return the last timestamp of this data buffer """
        if len(self._timestamps) > 0:
            return self._timestamps[-1]
        else:
            return 0