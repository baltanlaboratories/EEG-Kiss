import logging
from root.core.processingthread import ProcessingThread

class DataConsumer( ProcessingThread ):
    """
    DataConsumer is an abstract class for processing data from a blackboard buffer
    Through ProcessingThread's processing_step(), this class polls for new data on a specified buffer
    A subclass should implement _process_data() to process this data further.
    """
    
    def __init__(self, blackboard, patterns):
        """
        @param blackboard:
            the blackboard with the buffers that will be polled by this DataConsumer
        @param patterns:
            the patterns corresponding to the data buffers containing the data that will be consumed
            patterns should either be a string or a list of strings
        """
        ProcessingThread.__init__( self )
        if not isinstance( patterns, list ):
            patterns = [ patterns ]
            
        self.logger = logging.getLogger()
            
        self.blackboard = blackboard
        self._patterns  = patterns
        self._counters  = [ 0 for _ in patterns ]
        
        self._max_nr_samples = 0
        
    def _process_data(self, pattern, data, timestamps):
        """
        this method is called at a constant interval with new samples from the specified pattern
        This method is supposed to be implemented by a subclass
        """
        raise NotImplementedError("Implement _process_data(self, pattern, data, timestamps) in subclass")
        
    def process_step(self):
        """
        Inherited from ProcessingThread
        This method is executed at a constant interval
        
        At this constant interval, data is collected and _process_data is called.
        """
        for index, pattern in enumerate(self._patterns):
            # Check for number of new samples
            counter = self.blackboard.get_count( pattern )
            
            nr_new_samples          = counter - self._counters[index] 
            self._counters[index]   = counter
            
            # Get data from blackboard
            blackboard_data = self.blackboard.get_data(pattern, nr_new_samples)
            
            data        = blackboard_data['data']
            timestamps  = blackboard_data['timestamps']
            
            if data and nr_new_samples > 0:
                if nr_new_samples > self._max_nr_samples:
                    self._max_nr_samples = nr_new_samples
                    # NOTE: This shows how deep a buffer was filled before getting the data.
                    #print 'max:', nr_new_samples
                
                dlen = len(data)
                tlen = len(timestamps)
                
                if dlen != tlen:
                    self.logger.log(logging.CRITICAL, (__file__, ": The amount of data samples and timestamps do not match. Len(data) = ", dlen, " Len(timestamps) = ", tlen))
                
                self._process_data( pattern, data, timestamps )
    
    def clear_buffers(self):
        for index, pattern in enumerate(self._patterns):
            self.blackboard.clear(pattern)
            self._counters[index] = 0
