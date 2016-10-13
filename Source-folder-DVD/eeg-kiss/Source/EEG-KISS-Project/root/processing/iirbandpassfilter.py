from scipy.signal               import lfilter_zi
import numpy                    as np
from mne.filter                 import construct_iir_filter, _check_method

from root.processing.iirfilter    import IIRFilter

def make_bandpass( Fs, highpass, lowpass ):    
    """ Taken from mne filter package
    """
    iir_params = _check_method('iir', None, [])

    Fs = float(Fs)
    Fp1 = float(highpass)
    Fp2 = float(lowpass)
    Fs1 = Fp1
    Fs2 = Fp2
    if Fs2 > Fs / 2:
        raise ValueError('Effective band-stop frequency (%s) is too high '
                         '(maximum based on Nyquist is %s)' % (Fs2, Fs / 2.))

    if Fs1 <= 0:
        raise ValueError('Filter specification invalid: Lower stop frequency '
                         'too low (%0.1fHz). Increase Fp1 or reduce '
                         'transition bandwidth (l_trans_bandwidth)' % Fs1)

    iir_params = construct_iir_filter(iir_params, [Fp1, Fp2], [Fs1, Fs2], Fs, 'bandpass')
     
    return iir_params['b'], iir_params['a']
        
class BandPassIIRFilter( IIRFilter ):
    def __init__(self, blackboard, pattern, sample_rate=256, highpass = 1, lowpass = 50 ):
        
        # TODO: Check whether only a single pattern is selected
        IIRFilter.__init__( self, blackboard, pattern )
            
        self._b, self._a = make_bandpass( sample_rate, highpass, lowpass )
        
        # create initial zi variable for filter
        self._zi = lfilter_zi(self._b, self._a)
        
        self._pat_extension = '/bpf%d_%d' % ( highpass, lowpass )