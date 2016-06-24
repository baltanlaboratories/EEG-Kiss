"""
PlotWidget as base class.
"""
import numpy as np
from root.core.blackboard               import Blackboard 
from root.core.dataconsumer             import DataConsumer
from root.core.observerpattern          import Subject
from root.core.constants                import PatternStrings

class BasePlot ( DataConsumer, Subject ):
    """ This class can be used as a Widget in a TKinter application.
    The data as read from the blackboard is shown on the plot
    show() should be called to update the content of the plot with the received data  
    start() should be called for it to start receiving data.
    """
    
    def __init__( self, blackboard, patterns, ax ):
        """
        @param blackboard:
            blackboard instance which contains the data that must be plotted
        @param patterns
            the patterns corresponding to the data buffers that must be plotted
        @param ax
            the pyplot Axis instance to draw the plots on
        """ 
        if not isinstance(blackboard, Blackboard):
            raise ValueError("blackboard should be Blackboard instance")
        
        if not isinstance(patterns, list):
            if isinstance(patterns, str):
                patterns = [patterns]
            else:
                raise ValueError("patterns should be string or list of strings")
            
        Subject.__init__( self )
        DataConsumer.__init__( self, blackboard, patterns )
            
        self.blackboard     = blackboard
        self._patterns      = patterns
        
        self.ax = ax 
            
        #Initial variables:
        self.plotConfig( length=512 )
        
        self.reset()
        self.changed = False
        
    
    def _update_ax(self):
        """
        Abstract method that must be implemented by concrete classes to actually plot the data
        This method should only do the drawing on the canvas. Not the calculations. These should be done in _process_plot_data()
        """
        raise NotImplementedError("Implement _update_ax(self) in subclass")
    
    def show( self ):
        """ 
        Method to update the plot with the data buffer
        Should be called sequentially from main thread
        If the data has not changed, the plot will not be updated
        """
        if self.changed:
            self._update_ax()   
            self.changed = False
        
    def _process_plot_data(self, pattern, data, timestamps):
        """
        Abstract method that must be implemented by concrete classes to actually plot the data
        This method should process the data, not draw it. Drawing should be done in _update_ax() 
        """
        raise NotImplementedError("Implement _process_plot_data(self, pattern, data) in subclass")
        
    def _process_data(self, pattern, data, timestamps):
        """
        Inherited method from DataConsumer 
        Adds new samples from blackboard to locally stored buffer 
        """
        self._plotbuffer[pattern] = (self._plotbuffer[pattern] + data)[-self._plotlength:]
        if timestamps:
            self._timestampbuffer[pattern] = (self._timestampbuffer[pattern] + timestamps)[-self._plotlength:]
        
        data            = self._plotbuffer[pattern]
#         if timestamps:
        timestamps  = self._timestampbuffer[pattern]
        _length         = len( data ) 

        self._plotbuffer[pattern] = data[-self._plotlength:] 
#         if timestamps:
        self._timestampbuffer[pattern] = timestamps[-self._plotlength:]

#         if _length > self._plotlength:
#             # plot the last <plotlength> samples
#             self._plotbuffer[pattern] = data[-self._plotlength:] 
#             if timestamps:
#                 self._timestampbuffer[pattern] = timestamps[-self._plotlength:] 
#         else:
#             # plot 0 line before signal starts
#             self._plotbuffer[pattern] = [ 0 for _ in range(self._plotlength - _length)] + data
#             if timestamps:
#                 self._timestampbuffer[pattern] = [ 0 for _ in range(self._plotlength - _length)] + timestamps

        if not self.changed:
            self.changed = True

        self._process_plot_data( pattern, data, timestamps )

#         self.notify_observers('update_time')

    def reset(self):
        """
        Reset the buffers and the ax for the plot window  
        """
        try:
            self.ax.cla()
        except Exception as e:
            print 'Exception BasePlot:', e
            raise e
        
        self._plotbuffer        = { pat: [0 for _ in range(self._plotlength)] for pat in self._patterns }
        self._timestampbuffer   = { pat: [0 for _ in range(self._plotlength)] for pat in self._patterns }
        self.ax.set_axis_bgcolor('black')
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def plotConfig( self, **args):
        """ 
        set configuration settings for the plotwindow
        @param length
            indicates how many samples to fit into the plot window
        """
        length = args.get('length', None)
        if length:
            if length > 0:
#                 print 'length: ', length
                self._plotlength = int(float(length))
                self.reset()
                
    def get_offset_last_samples(self):
        values = []
        for pat in self._patterns:
            if PatternStrings.MARKERS not in pat:
#                print("calculate mean of pattern: ", pat)
                length = len(self._plotbuffer[pat])
                if length>200:
                    length = 200
#                print ("Length: ", length)
#                print ("Last samples: ", self._plotbuffer[pat][-length:])
                sub_array = self._plotbuffer[pat][-length:]
                if len(sub_array)>0:
                    min_value = min(self._plotbuffer[pat][-length:])
                    max_value = max(self._plotbuffer[pat][-length:])
#                    print ("tmp min value: ", min_value)
                    values.append((max_value-min_value)/2+min_value)
                    
        if len(values)>0:
            return min(values)
        else:
            return 0