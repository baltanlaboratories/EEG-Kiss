# Authors: Denis Engemann <denis.engemann@gmail.com>
#
# License: BSD (3-clause)
from matplotlib.pyplot import imshow

print(__doc__)

import numpy as np
import matplotlib.pyplot as plt

import mne
from mne import io
from mne.datasets import sample
from mne.io.pick import pick_types
from mne.parallel import parallel_func

from root.input.hdfreader import HDFReader
from root.data import filenames

def _compute_psd(data, fmin, fmax, Fs, n_fft, psd, n_overlap, pad_to):
    """Compute the PSD"""
    out = [psd(d, Fs=Fs, NFFT=n_fft, noverlap=n_overlap, pad_to=pad_to)
           for d in data]
    psd = np.array([o[0] for o in out])
    freqs = out[0][1]
    mask = (freqs >= fmin) & (freqs <= fmax)
    freqs = freqs[mask]
    return psd[:, mask], freqs

n_fft = 256  # the FFT size. Ideally a power of 2

fmin=0
fmax=200
pad_to=None
n_overlap=0
Fs = 256

# Initialize data reader
reader = HDFReader();
 
def sins( leng, freqs, amps, sample_rate=256 ):
    import math
    if len(freqs) == len(amps):
        return [ sum([ amps[j] * math.sin( freqs[j] * 2 * math.pi * i / sample_rate ) for j in range(len(freqs)) ]) for i in range(leng) ]

# Reading two datafiles
[ mat, frequencies ] = reader.read( filenames[7][0] )       # Read data from first data file
_data = np.asarray( mat[1][1] )       # get data from selected channels

bufsize = 256

_data = [ _data[i:i+bufsize] for i in range(0,len(_data),bufsize) ]
print 'len', len(_data)

import matplotlib.pyplot as plt

out = [ _compute_psd(data, fmin, fmax, Fs, n_fft, plt.psd, n_overlap, pad_to) for data in [_data] ]
plt.close()

psds = [o[0] for o in out]
freqs = [o[1] for o in out]

psds = np.array(psds)
freqs = freqs[0]

some_psds = 10 * np.log10(psds[0])

freq_mask = freqs < 50
freqs = freqs[freq_mask]

# fig = plt.Figure( figsize=(1,1), dpi=100 )
fig = plt.figure( )
fig.set_facecolor('black')
# ax1 = fig.add_axes( [0,0,1,1] )
axim = plt.imshow([[ 0 for _ in range(165) ] for _ in range(50) ], aspect='auto', origin='lower')
# axim = plt.imshow(some_psds[:, freq_mask].T, aspect='auto', origin='lower')
     
plt.ion() 

plt.show()

# fig, (ax1) = plt.subplots(1, 1, sharex=True, sharey=True, figsize=(10, 5) )
# ax1.set_position( [0.1,0,1,1] )

# fig.suptitle('Single trial power', fontsize=12)

# ax1.set_title('single trial', fontsize=10)
# ax1.set_yticks(np.arange(0, len(freqs), 10))
# ax1.set_yticklabels(freqs[::10].round(0))
# ax1.set_ylabel('Frequency (Hz)')

print 'update image'
img_dat = some_psds[:, freq_mask].T
axim.set_clim(img_dat.min(),img_dat.max())
axim.set_array( img_dat )

plt.pause(0.1)
plt.draw()





