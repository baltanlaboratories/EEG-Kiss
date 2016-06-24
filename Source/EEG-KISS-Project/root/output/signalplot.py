from root.output.baseplot import BasePlot
import numpy as np
from pip._vendor.progress.spinner import LineSpinner

class SignalPlot ( BasePlot ):
    """
    SignalPlot is the most basic plot class. 
    Shows a number of 2D lines on a given Axis instance.
    start() must be called for it to be able to receive data.
    """

    """
    Predefined colors for the plot-lines
    """
    colors = ['w', 'y', 'r']
    
    def __init__( self, blackboard, patterns, ax, name='No name provided for SignalPlot', showLabel=False ):
        """
        Initializes the initial values for y-limits and other attributes
        @param blackboard:
            blackboard instance which contains the data that must be plotted
        @param patterns
            the patterns corresponding to the data buffers that must be plotted
        @param ax
            the pyplot Axis instance to draw the plots on
        """
        self.xLim = 0
        self.yoffset = 2000
        self.ymin = self.yoffset - 4000
        self.ymax = self.yoffset + 4000
        self.label = name
        self.showlabel= showLabel
        BasePlot.__init__(self, blackboard, patterns, ax ) 
        self.reset()
             
    def _update_ax( self ):
        """
        Inherited from BasePlot
        Prepends zeroes if there is not enough data in the buffer
        Sets the new data for each line   
        """
        for pattern, line in zip( self._patterns, self.ax.get_lines() ):
            data = self._plotbuffer[pattern]
            _length = len( data ) 
            if _length > self._plotlength:
                # plot the last <plotlength> samples
                data = data[-self._plotlength:] 
            else:
                # plot 0 line before signal starts
                data = [ 0 for _ in range(self._plotlength - _length)] + data
                
            y = data
            
            line.set_data( self._x, y )
          
    def _process_plot_data(self, pattern, data, timestamps):
        """
        Inherited from BasePlot
        Called when data is appended to buffer
        Sets line width to non-zero so plot-line is visible.
        @param pattern:
            pattern for line which data is appended
        @param data:
            the appended data
        """
        # TODO: delete this part. Only register patterns that contain data.
        lines = [ line for line, pat in zip(self.ax.get_lines(), self._patterns) if pat == pattern ]
        if lines != []:
            lines[0].set_linewidth( 1 )
            
    def reset(self):
        """
        Overrides BasePlot method. Therefore calls it as super.
        Resets the plot lines and ranges
        Initializes lines with zero-width so they will not be visible.
        """
        BasePlot.reset( self )
        self._x = np.linspace(0,1, self._plotlength)
        # TODO: dont'init lines with linewidth=0
        try:    
            for index in range(len(self._patterns)):
                self.ax.plot( [],[],color=self.colors[index%len(self.colors)], linewidth=0, label=self.label)

            self.ax.set_xlim( [ self.xLim, 1 ] )
            self.ax.set_ylim( [ self.ymin, self.ymax ] )
        except Exception as e:
            print 'Exception SignalPlot:', e
            raise e
        
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
        """
        BasePlot.plotConfig( self, **args )

        yoffset = args.get('yoffset', None)
        if not yoffset == None:
            self.yoffset = yoffset
            #print 'yoffset:', yoffset
        
        yrange = args.get('yrange', None)
        if not yrange == None:
            self.yrange = yrange

        if not yoffset == None or not yrange == None:
            self.ymax = self.yoffset + self.yrange 
            self.ymin = self.yoffset - self.yrange
            self.ax.set_ylim( [self.ymin, self.ymax] )
        
# TODO: To be backwards compatible (play old records), this might need to be fixed (next code has been changed/moved to 'plotConfig' of 'TimedSignalPlot'):
#         xLim = args.get('xLim', None)
#         if xLim is not None:
#             #print 'xLim: ', xLim
#             self.xLim = xLim
#             [ left, right ] = self.ax.set_xlim( [ xLim, 1 ] )
#             #print left, right
