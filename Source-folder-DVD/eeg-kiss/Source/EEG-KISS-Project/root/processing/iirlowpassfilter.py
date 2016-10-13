from scipy.signal               import lfilter_zi
import numpy                    as np
from mne.filter                 import construct_iir_filter, _check_method

from root.processing.iirfilter    import IIRFilter

class IIRLowPassFilter( IIRFilter ):
    """
    IIRLowPassFilter is a simple type of linear filter
    It is based on IIR parameter calculation from the MNE library which uses SciPy
    """
    
    def __init__(self, blackboard, pattern, sample_rate=256, lowpass = 50 ):
        """
        @param blackboard:
            blackboard instance which contains the data that must be plotted.
        @param pattern
            the pattern corresponding to the data buffer that must be filtered. Only one pattern should be selected.
        @param sample_rate
            sample rate of the data signal. Should be a positive numerical value.
        @param lowpass
            The filter's cutoff-frequency. Should be a positive numerical value.
        """
        IIRFilter.__init__( self, blackboard, pattern )
            
        self._b, self._a = self._make_lowpass( sample_rate, lowpass )
        
        # create initial zi variable for filter
        self._zi = lfilter_zi(self._b, self._a)
        
        self._pat_extension = '/lpf%d' % ( lowpass )
        
        
    def _make_lowpass( self, Fs, lowpass ):    
        """ 
        Taken from mne filter package
        Generates IIR A and B parameters based on the sample frequency and the cutoff frequency 
        """
        iir_params  = _check_method('iir', None, [])
    
        Fs          = float(Fs)
        lowpass     = float(lowpass)
        if lowpass > Fs / 2.:
            raise ValueError('Effective stop frequency (%s) is too high '
                             '(maximum based on Nyquist is %s)' % (lowpass, Fs / 2.))
    
        iir_params = construct_iir_filter(iir_params, lowpass, lowpass, Fs, 'low')
         
        return iir_params['b'], iir_params['a']
        