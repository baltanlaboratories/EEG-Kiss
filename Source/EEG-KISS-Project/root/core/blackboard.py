from blackboardbuffer import BlackboardBuffer
from root.core.circularbuffer import CircularBuffer
from root.core.constants import BufferTypes
from root.core.ordinarybuffer import OrdinaryBuffer
from _collections import defaultdict

class Blackboard:
    """ 
    The blackboard holds a number of data buffers which have to be accessible by a number of different threads at the same time.
    Each data patterns (buffer names) must be registered before the can be read. 
    If a pattern is not registered it is ignored when put.
    Each buffer has a corresponding count value which counts the total number of processed samples
    """
    def __init__(self):
        self.buffers = {}
    
    def _check(self, pattern, bufferType):
        if not pattern in self.buffers:
            if bufferType == BufferTypes.ORIGINAL:
                self.buffers[pattern] = BlackboardBuffer( pattern )
            elif bufferType == BufferTypes.CIRCULAR:
                self.buffers[pattern] = CircularBuffer( pattern )
            elif bufferType == BufferTypes.ORDINARY:
                self.buffers[pattern] = OrdinaryBuffer( pattern )
            else:
                raise NotImplementedError("You're using an unknown bufferType")
    
    def put_data( self, pattern, value, timestamp = None, buftype = BufferTypes.CIRCULAR):
        """
        Add data to a specified buffer.
        If pattern is not yet registered, a new buffer is created for this pattern.
        NOTE: By default a circular buffer is created.
        @param pattern:
            Name of the buffer to add the data to
        @param value:
            The data-value(s) to be added.
        @param timestamp:
            The timestamp-value(s) to be added.
        @param buftype:
            The type of buffer to be created for this data.
        """
        self._check( pattern, buftype )
        self.buffers[pattern].put_data( value, timestamp )
        
    def put_fft( self, pattern, freqs, fft):
        """
        Add freqs and fft to a specified buffer.
        If pattern is not yet registered, a new buffer is created for this pattern.
        NOTE: This method always creates an ordinary buffer.
        @param pattern:
            Name of the buffer to add the data to
        @param freqs:
            The frequency to be added. Assumed to be a list
        @param fft:
            The result of fft to be added. Assumed to be a list
        """
        self._check( pattern, BufferTypes.ORDINARY)
        self.buffers[pattern].put_data( freqs, fft )
    
    def get_data(self, pattern, count = None):
        """
        Returns the data of a specified buffer or empty data if pattern is not registered or if no data available for given pattern.
        NOTE: Only data from circular or original blackboard buffers can be returned.
        """        
        buf = self.buffers.get( pattern, None )
        
        if buf:
            if isinstance(buf, CircularBuffer) or isinstance(buf, BlackboardBuffer):
                return buf.get_data(count)     
            
        return defaultdict(list, data=[], timestamps=[])
        #return [], []
    
    def get_data_window(self, pattern, first, last):
        """ Returns the timestamps of a specified buffer or None if it is not registered """
        buf = self.buffers.get( pattern, None )
        if buf and not last==0:
            return buf.get_data_window(first, last)
        return None
    
    def get_timestamps(self, pattern, count = None):
        """ Returns the timestamps of a specified buffer or None if it is not registered """
        buf = self.buffers.get( pattern, None )
        if buf:
            if isinstance(buf, CircularBuffer):
                return buf.get_timestamps(count)
        return None
    
    def get_timestamps_window(self, pattern, first, last):
        """ Returns the timestamps of a specified buffer or None if it is not registered """
        buf = self.buffers.get( pattern, None )
        if buf:
            return buf.get_timestamps_window(first, last)
        return None
    
    def get_freq(self, pattern):
        """ Returns the frequencies of a specified buffer or None if it is not registered """
        buf = self.buffers.get( pattern, None )
        
        if buf:
            if isinstance(buf, OrdinaryBuffer):
                return buf.get_xaxes()
        return None
    
    def get_fft(self, pattern):
        """ Returns the fft-values of a specified buffer or None if it is not registered """
        buf = self.buffers.get( pattern, None )
        
        if buf:
            if isinstance(buf, OrdinaryBuffer):
                return buf.get_yaxes()
        return None
    
    def get_patterns(self):
        return self.buffers.keys()
    
    def get_count(self, pattern):
        """ Returns a specified buffer counter or -1 if it is not registered """
        buf = self.buffers.get( pattern, None )
        if buf:
            return buf.get_count()
        return -1
    
    def clear(self, pattern):
        """ Clear one specified buffer """
        buf = self.buffers.get( pattern, None )
        if buf:
            buf.clear()
    
    def set_bufsize(self, pattern, size, buftype = BufferTypes.CIRCULAR):
        """ Set buffer size for a specified buffer """
        self._check( pattern, buftype )
        self.buffers[pattern].set_bufsize( size )
        
    def get_last_timestamp(self, pattern):
        """ return the last timestamp of the data buffer with given pattern """
        buf = self.buffers.get( pattern, None )
        if buf:
            return buf.get_last_timestamp()
        
        return 0
    
    def get_bufsize(self, pattern):
        """ Returns length of specified buffer """
        buf = self.buffers.get( pattern, None )
        if buf:
            return buf.get_bufsize()
        return -1