'''
Created on Jul 16, 2015

@author: tim.hermans
'''
from root.core.processingthread import ProcessingThread

class SyncDataConsumer(ProcessingThread):
    '''
    SyncDataCostumer is an abstract class for processing data from the blackboard buffers
    Through ProcessingThread's processing_step(), this class polls for new data on a specified buffer
    A subclass should implement _process_data() to process this data further.
    '''


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
            patterns in [ patterns ]
        
        self.blackboard = blackboard
        self._patterns  = patterns
        self._lastTimestamp  = None
        
    def _process_data(self, pattern, data, timestamps):
        """
        this method is called at a constant interval with new samples from the specified patterns
        This method is supposed to be implemented by a subclass
        """
        raise NotImplementedError("Implement _process_data(self, pattern, data, timestamps) in subclass")
    
    def process_step(self):
        """
        Inherited from ProcessingThread
        This method is executed at a constant interval
        
        At this constant interval, data is collected and _process_data is called.
        """
        timestamps = []
        for pattern in self._patterns:
            tmp = self.blackboard.get_last_timestamp(pattern)
            timestamps.append(tmp)
            
        lastSharedTimestamp = min(timestamps)
        
        if not self._lastTimestamp == lastSharedTimestamp:
            #print "last ", self._lastTimestamp, " shared ", lastSharedTimestamp
            data = {}
            timestamps = []
            
            for pattern in self._patterns:
                tmp = self.blackboard.get_data_window(pattern, self._lastTimestamp, lastSharedTimestamp)
                if tmp and len(tmp) > 0:
                    data[pattern] = tmp
            
            if len(data) == len(self._patterns):
                timestamps = self.blackboard.get_timestamps_window(self._patterns[0], self._lastTimestamp, lastSharedTimestamp)
                self._lastTimestamp = lastSharedTimestamp
                self._process_data(self._patterns, data, timestamps)
    
    def clear_buffers(self):
        self._lastTimestamp  = None
        for pattern in self._patterns:
            self.blackboard.clear(pattern)
                