import numpy as np
from math import pi
from scipy.fftpack import fft, ifft
from matplotlib import pyplot as plt

# create a wave with 1Mhz and 0.5Mhz frequencies
dt = 40e-9
t = np.arange(0, 1000e-6, dt)
fscale = t/max(t)
y = np.cos(2 * pi * 1e6 * t*fscale) + (np.cos(2 * pi * 2e6 *t*fscale) * np.cos(2 * pi * 2e6 * t*fscale))
y *= np.hanning(len(y))
yy = np.concatenate((y, ([0] * 10 * len(y))))

# FFT of this
Fs = 1 / dt  # sampling rate, Fs = 500MHz = 1/2ns
n = len(yy)  # length of the signal
k = np.arange(n)
T = n / Fs
frq = k / T  # two sides frequency range
frq = frq[range(n / 2)]  # one side frequency range
Y = fft(yy) / n  # fft computing and normalization
Y = Y[range(n / 2)] / max(Y[range(n / 2)])

# plotting the data
plt.subplot(3, 1, 1)
plt.plot(t * 1e3, y, 'r')
plt.xlabel('Time (micro seconds)')
plt.ylabel('Amplitude')
plt.grid()

# plotting the spectrum
plt.subplot(3, 1, 2)
plt.plot(frq[0:600], abs(Y[0:600]), 'k')
plt.xlabel('Freq (Hz)')
plt.ylabel('|Y(freq)|')
plt.grid()

# plotting the specgram
ax = plt.subplot(3, 1, 3)
Pxx, freqs, bins, im = ax.specgram(y, NFFT=512, Fs=Fs, noverlap=10)
plt.show()