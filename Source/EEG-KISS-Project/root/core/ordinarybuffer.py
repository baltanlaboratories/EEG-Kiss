import numpy

class OrdinaryBuffer:
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
        self._xaxes       = []
        self._yaxes       = []
        self._pattern     = pattern
    
    ### METHODS ###
    def put_data(self, xaxes, yaxes):
        """
        Replace data of the buffer
        @param xaxes:
            list of values for the x-axes
        @param yaxes:
            list of values for the y-axes  
        """
        if not isinstance(xaxes, list):
                xaxes = [xaxes]
        if not isinstance(yaxes, list):
                yaxes = [yaxes]
                
        self.clear()
        
        for x in xaxes:
            self._xaxes.append( x )
            self._count += 1
            
        for y in yaxes:
            self._yaxes.append( y )
      
    def get_xaxes(self):
        """ Returns the data from this buffer """
        return self._xaxes
    
    def get_yaxes(self):
        """ Returns the data from this buffer """
        return self._yaxes
    
    def clear(self):
        """ remove all collected data """
        self._xaxes = []
        self._yaxes = []
        self._count = 0
               
    ### GETTERS ###    
    def get_count(self):
        """ Returns the sample counter of this data buffer"""
        return self._count
    
    def get_pattern(self):
        """ returns the pattern of this data buffer """
        return self._pattern
