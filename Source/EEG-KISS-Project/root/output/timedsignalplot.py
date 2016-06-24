'''
Created on 19 mei 2015

@author: Bas.Kooiker
'''
from root.output.signalplot import SignalPlot
from root.output.baseplot import BasePlot
from root.core.constants import Markers

class TimedSignalPlot( SignalPlot ):
    
    def __init__( self, blackboard, patterns, ax, marker_pattern=None, name='No name provided for TimedSignalPlot', showLabel=False ):
        self.marker_pattern = marker_pattern
        if marker_pattern:
            patterns.append( marker_pattern )
        SignalPlot.__init__( self, blackboard, patterns, ax, name, showLabel )
        self.reset()
    
    def _update_ax( self ):
        """
        Inherited from BasePlot
        Prepends zeroes if there is not enough data in the buffer
        Sets the new data for each line   
        """
        for pattern, line in zip( self._patterns , self.ax.get_lines() ):
            x = self._timestampbuffer[pattern]
            y = self._plotbuffer[pattern]
            
            #print zip(x, y)

            if len(x) == len(y): 
                line.set_data( x, y )
            else:
                print 'len(x): ' + str(len(x))
                print 'len(y): ' + str(len(y))

        xUp = self.xUpper
        lim = [ xUp - (.5 + (1 - self.xLim) * 20), xUp ]
        self.ax.set_xlim( lim )
    
    def _process_data(self, pattern, data, timestamps):
        if pattern == self.marker_pattern:
            i = int(data[0])
            while self.changed:
                pass
            self.ax.axvline(x = timestamps[0], color = Markers.Color[i])
            self.changed = True
        else:
            BasePlot._process_data( self, pattern, data, timestamps )
        
    def reset(self):
        SignalPlot.reset(self)
        self.xUpper = 0
        self._plotbuffer        = { pat: [] for pat in self._patterns }
        self._timestampbuffer   = { pat: [] for pat in self._patterns }

    def plotConfig(self, **args):
        SignalPlot.plotConfig(self, **args)

        xUpper = args.get('xUpper', None)
        if xUpper:
            self.xUpper = xUpper
        
        xLim = args.get('xLim', None)
        if xLim is not None:
            self.xLim = xLim
            lim = [ self.xUpper - (.5 + (1 - self.xLim) * 20), self.xUpper ]
            self.ax.set_xlim( lim )
