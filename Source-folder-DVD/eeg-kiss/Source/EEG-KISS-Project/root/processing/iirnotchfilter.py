from scipy.signal               import lfilter_zi
import numpy                    as np
from mne.filter                 import construct_iir_filter, _check_method

from root.processing.iirfilter    import IIRFilter

def make_notch( Fs, center, width=1 ):
    # Assure lower boundary is not too low
    Fp1 = max(center-width/2., 0.1)
    Fp2 = center+width/2.

    iir_params = _check_method('iir', None, [])

    Fp1 = np.atleast_1d(Fp1)
    Fp2 = np.atleast_1d(Fp2)
    if not len(Fp1) == len(Fp2):
        raise ValueError('Fp1 and Fp2 must be the same length')

    Fs = float(Fs)
    Fp1 = Fs1 = Fp1.astype(float)
    Fp2 = Fs2 = Fp2.astype(float)

    if np.any(Fs1 <= 0):
        raise ValueError('Filter specification invalid: Lower stop frequency '
                         'too low (%0.1fHz). Increase Fp1 or reduce '
                         'transition bandwidth (l_trans_bandwidth)' % Fs1)

    for fp_1, fp_2, fs_1, fs_2 in zip(Fp1, Fp2, Fs1, Fs2):
        iir_params_new = construct_iir_filter(iir_params, [fp_1, fp_2],
                                              [fs_1, fs_2], Fs, 'bandstop')
        
        
    iir_params_new = dict(order=4, ftype='butter')
    iir_params_new = construct_iir_filter(iir_params, [center-1, center], [center, center+1], Fs, 'bandstop', return_copy=False)
    
#     b, a = signal.butter(2,bp_stop_Hz/(fs_Hz / 2.0), 'bandstop')
    
    return iir_params_new['b'], iir_params_new['a']
        
class IIRNotchFilter( IIRFilter ):
    
    def __init__(self, blackboard, pattern, sample_rate=256, cutoff_freq=50, cutoff_width = 2):
        
        # TODO: Check whether only a single pattern is selected
        IIRFilter.__init__( self, blackboard, pattern )
            
        # use 10 Hz notch instead
        self._b, self._a = make_notch( sample_rate, cutoff_freq, cutoff_width )
        
        # create initial zi variable for filter
        self._zi = lfilter_zi(self._b, self._a)
        
        self._pat_extension = '/notch%d' % ( cutoff_freq )