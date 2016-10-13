import math

from scipy.signal           import butter, filtfilt, lfilter_zi, lfilter
from random                 import randint
import matplotlib.pyplot    as plt
import numpy                as np

from mne.filter             import construct_iir_filter, _check_method 

def noise( leng, freq=1, sample_rate = 256, amp = 1, noise = 1 ):
    return [ amp * math.sin( freq * 2 * math.pi * i / sample_rate) + noise * randint( 0, 2000 ) / 1000 - 1 for i in range(leng) ]

def sins( leng, freq1=1, freq2=10, amp1=1, amp2=1, sample_rate=256 ):
    return [ amp1 * math.sin( freq1 * 2 * math.pi * i / sample_rate) + amp2 * math.sin( freq2 * 2 * math.pi * i / sample_rate)  for i in range(leng) ]

def make_notch( Fs, center, width=1 ):
    Fp1 = center-width/2.
    Fp2 = center+width/2.

    iir_params = _check_method('iir', None, [])
    print iir_params

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
        return iir_params_new['b'], iir_params_new['a']
        

if __name__ == '__main__':
    # 1 seconds of data
#     data = noise(256, freq = 10, amp = 5)
    data_length = 2560
    data = sins( data_length )
    
    # use 10 Hz notch instead
    b, a = make_notch( 256, 10 )
    
    # create initial zi variable for filter
    zi = lfilter_zi(b, a)
    
    # actually filter the data
    results_1 = []
    for x in data:
        y, zi = lfilter(b, a, [x], zi=zi)
        results_1.append( y )
    
    sin1 = sins( data_length, amp2=0)
    
    diff = [abs(x - y) for x,y in zip(results_1, sin1) ]
    
#     plt.plot( data, linewidth=.5 )
    plt.plot( results_1, linewidth=.5 )
#     plt.plot( sin1, linewidth=.5 )
#     plt.plot( diff, linewidth=.5 )

    plt.show()

        
    