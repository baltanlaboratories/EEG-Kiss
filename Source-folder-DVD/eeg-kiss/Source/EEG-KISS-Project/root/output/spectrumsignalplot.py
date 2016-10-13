from root.output.baseplot import BasePlot
import numpy as np
from root.core.fftconsumer import FftConsumer
from root.core.observerpattern import Subject
from root.core.blackboard import Blackboard
from root.core.constants import PatternStrings

class SpectrumSignalPlot ( FftConsumer, Subject ):
    """
    FrequencyPlot is the most basic plot class. 
    Shows a number of 2D lines on a given Axis instance.
    start() must be called for it to be able to receive data.
    """

    """
    Predefined colors for the plot-lines
    """
    colors = ['w', 'y', 'r']
    
    def __init__( self, blackboard, patterns, ax, name='No name provided for FrequencyPlot', showLabel=False ):
        """
        Initializes the initial values for y-limits and other attributes
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
        FftConsumer.__init__( self, blackboard, patterns )
            
        self.blackboard     = blackboard
        self._patterns      = patterns
        self.ax = ax 
        
        
        self.xLim = 64
        self.yoffset = 250
        self.ymin = self.yoffset - 2000
        self.ymax = self.yoffset + 2000
        self.label = name
        self.showlabel= showLabel
        self._plotlength =128
        self.changed = False
        self.reset()
             
    def _update_ax( self ):
        #Sets the new data for each line
        
        for pattern, line in zip( self._patterns , self.ax.get_lines() ):
            line.set_data( self._freq[pattern], self._fft[pattern] )
    
    def show( self ):
        """ 
        Method to update the plot with the data buffer
        Should be called sequentially from main thread
        If the data has not changed, the plot will not be updated
        """
        if self.changed:
            self._update_ax()   
            self.changed = False
            
    def _process_data(self, pattern, freq, fft):
        """
        Inherited from BasePlot
        Called when data is appended to buffer
        Sets line width to non-zero so plot-line is visible.
        @param pattern:
            pattern for line which data is appended
        @param freq:
            the frequency data
        @param fft:
            the fft data
        """        
        self.changed = True
        
        self._freq[pattern]=freq
        self._fft[pattern]=fft
        
        lines = [ line for line, pat in zip(self.ax.get_lines(), self._patterns) if pat == pattern ]
        if lines != []:
            lines[0].set_linewidth( 1 )
            
    def reset(self):
        self.ax.cla()
        self.ax.set_axis_bgcolor('black')
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self._freq   = { pat: [] for pat in self._patterns }
        self._fft    = { pat: [] for pat in self._patterns }
        # TODO: dont'init lines with linewidth=0
        for index in range(len(self._patterns)):
            self.ax.plot( [],[],color=self.colors[index%len(self.colors)], linewidth=0, label=self.label)
            
        self.ax.set_xlim( [ 0, self.xLim ] )
        self.ax.set_ylim( [ self.ymin, self.ymax ] )
        
        if self.showlabel:
            handles, labels = self.ax.get_legend_handles_labels()
            self.ax.legend([handles[0]], [labels[0]])
            legend=self.ax.get_legend()
            for text in legend.get_texts():
                text.set_color('w')
            frame = legend.get_frame()
            frame.set_facecolor('black')
            frame.set_linewidth(0)

    def plotConfig( self, **args ):
        """ 
        set configuration settings for the plotwindow
        @param length
            indicates how many samples to fit into the plot window
        @param yoffset
            indicates the offset for the y-axis
        @param yrange
            indicates the range for the y-axis
        @param length
            indicates how many samples to fit into the plot window
        """
       
        """ Length of plot is fixed !!!
        length = args.get('length', None)
        if length:
            if length > 0:
                self._plotlength = int(float(length))"""
                
        xlim = args.get('xLim', None)
        if xlim:
            if xlim > 0:
                self.ax.set_xlim([0, int(float(xlim))])

        yoffset = args.get('yoffset', None)
        if yoffset:
            self.yoffset = yoffset
        
        yrange = args.get('yrange', None)
        if yrange:
            self.yrange = yrange

        if yoffset or yrange:
            self.ymax = self.yoffset + self.yrange 
            self.ymin = self.yoffset - self.yrange
            self.ax.set_ylim( [self.ymin, self.ymax] )
            
    def get_offset_last_samples(self):
        values = []
        for pat in self._patterns:
            if PatternStrings.MARKERS not in pat:
                length = len(self._fft[pat])
                if length>1:
                    #Do not use [0] This is the DC component and is to high
                    min_value = min(self._fft[pat][1:])
                    max_value = max(self._fft[pat][1:])
                    values.append((max_value-min_value)/2+min_value)
                    
        if len(values)>0:
            return min(values)
        else:
            return 0