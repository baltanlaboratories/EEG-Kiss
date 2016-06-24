'''
Created on 1 mei 2015

@author: Bas.Kooiker
'''

from scipy                      import signal
from scipy.signal.signaltools   import lfilter

from root.core.dataconsumer     import DataConsumer

class FIRFilter( DataConsumer ):
    
    def __init__(self, blackboard, pattern, numtaps, Fs, frequencies, type='lpf' ):
        """
        @param blackboard:
            blackboard instance which contains the data that must be plotted.
        @param pattern
            the pattern corresponding to the data buffer that must be filtered. Only one pattern should be selected.
        @param numtaps
            number of coefficients for FIR filter
        @param Fs
            Sample rate of signal
        @param frequencies
            cutoff frequency (or frequencies) for filter. Depending on the type, one or two frequencies should be supplied.
        @param filtertype. 
            Choose from: 'lpf','hpf','bpf','bsf','notch'
        """
        if not type in ['lpf','hpf','bpf','bsf','notch']:
            raise TypeError( 'Incompatible filter type.' )
            
        if isinstance( pattern, list ):
            if len( pattern ) == 1:
                pattern = pattern[0]
        if not isinstance( pattern, str ):
            raise TypeError( 'Incompatible pattern type. Should be a single string.' )
        
        DataConsumer.__init__(self, blackboard, [pattern] )
        
        if not isinstance(frequencies, list):
            frequencies = [ frequencies ]
        
        self._pat_extension = '/%s'%type
        for f in frequencies:
            self._pat_extension += '_%d' % f
        
        width = 10
        nyq = Fs/2
        
        if type == 'lpf':
            f1 = (frequencies[0]-width/2) / (.5 * Fs)
            self._coefficients = signal.firwin( numtaps, [f1] )
        elif type == 'notch':
            f1 = (frequencies[0]-width/2) / (.5 * Fs)
            f2 = (frequencies[0]+width/2) / (.5 * Fs)
            self._coefficients = signal.firwin( numtaps, [f1, f2] )
        else:
            raise NotImplementedError('Filter types will soon be implemented')
            
        self._buffer = []
            
    def _process_data(self, pattern, data, timestamps ):
        """
        Inherited from DataConsumer.
        Buffers the incoming signal and returns the filtered data to the blackboard
        """
        for d,t in zip(data,timestamps):
            self._buffer.append(d)
            self._buffer = self._buffer[-len(self._coefficients):]
            result = lfilter( self._coefficients, 1, self._buffer )[-1]
            self.blackboard.put_data(pattern+self._pat_extension, result, t )
            
    def get_coefficients(self):
        """
        Getter for coefficients
        """
        return self._coefficients