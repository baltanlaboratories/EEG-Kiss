from root.core.processingthread import ProcessingThread

class FftConsumer( ProcessingThread ):
    """
    FftConsumer is an abstract class for processing data from a blackboard buffer
    Through ProcessingThread's processing_step(), this class polls for new data on a specified buffer
    A subclass should implement _process_data() to process this data further.
    """
    
    def __init__(self, blackboard, patterns, suppressDC=True):
        """
        @param blackboard:
            the blackboard with the buffers that will be polled by this FftConsumer
        @param patterns:
            the patterns corresponding to the data buffers containing the data that will be consumed
            patterns should either be a string or a list of strings
        """
        ProcessingThread.__init__( self )
        if not isinstance( patterns, list ):
            patterns in [ patterns ]
            
        self.blackboard     = blackboard
        self._patterns      = patterns
        self._previous      = [ [] for _ in patterns ]
        self._suppressDC      = suppressDC
        
    def _process_data(self, pattern, freq, fft):
        """
        this method is called at a constant interval with new samples from the specified pattern
        This method is supposed to be implemented by a subclass
        """
        raise NotImplementedError("Implement _process_data(self, pattern, freq, fft) in subclass")
        
    def process_step(self):
        """
        Inherited from ProcessingThread
        This method is executed at a constant interval
        
        At this constant interval, data is collected and _process_data is called.
        """
        for index, pattern in enumerate(self._patterns):         
            # Get data from blackboard
            freq = self.blackboard.get_freq(pattern)
            fft = self.blackboard.get_fft(pattern)

            if freq and fft:
                if not fft == self._previous[index]:
                    self._previous[index]=fft
                    if self._suppressDC:
                        fft[0] = 0
                    self._process_data( pattern, freq, fft )
    
    def reset_datacounters(self):
        for index, pattern in enumerate(self._patterns):
            self._previous[index] = []

    def clear_buffers(self):
        for index, pattern in enumerate(self._patterns):
            self.blackboard.clear(pattern)
            self._previous[index] = []
