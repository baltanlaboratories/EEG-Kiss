from scipy.signal                   import lfilter
from root.core.dataconsumer   import DataConsumer

class IIRFilter( DataConsumer ):
    """
    A Linear filter is used to process a one-dimensional, constant frequency, data signal.
    It's based on SciPy's lfilter() method.
    Implements DataConsumer to continuously scan one blackboard buffer for new data and process it with _process_data() 
    """
    
    def __init__(self, blackboard, pattern):
        """
        @param blackboard:
            blackboard instance which contains the data that must be plotted.
        @param pattern
            the pattern corresponding to the data buffer that must be filtered. Only one pattern should be selected.
        """
        
        if isinstance( pattern, list ):
            if len( pattern ) == 1:
                pattern = pattern[0]
        if not isinstance( pattern, str ):
            raise TypeError( 'Incompatible pattern type. Should be a single string.' )
        
        DataConsumer.__init__(self, blackboard, [pattern] )
        
        self._pat_extension = None
        self._b             = None
        self._a             = None
        self._zi            = None
        
    
    def _process_data(self, pattern, data, timestamps ):
        """
        Inherited from DataConsumer.
        @param pattern
            The pattern corresponding to the data's buffer
        @param data
            The new data samples, which are not processed yet.
        """
        for d in data:
            result, self._zi = lfilter(self._b, self._a, [d], zi=self._zi)
            self.blackboard.put_data(pattern+self._pat_extension, result[0] )
                                 