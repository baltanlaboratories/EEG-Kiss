'''
Created on Apr 1, 2015

@author: Sjors.Ruijgrok

Some example code for getting the frequency-spectrum from a signal in time-domain.

Example1 shows the FFT of 2 added sinus-signals.
Example2 shows the FFT of 2 added sinus-signals with extra noise added.
Example3 shows the FFT of a signal recorded with the EEG-headset. 

File "test1.hdf5" was recorded while the headset was just laying on table (so it's just noise with 50 Hz component
picked up from environment).
File "test2.hdf5" is the EEG-signal recorded with the headset on my head.

Before applying FFT the DC-component is removed from the signal to filter out the 0 Hz component.
'''

from scipy import pi
from scipy import sin
from scipy import signal
from scipy.fftpack import fft
from scipy.fftpack import fftfreq
import numpy as np
import matplotlib.pyplot as plt
from root.input.hdfreader import HDFReader

TEST_FILE_1 = 'test1.hdf5'
TEST_FILE_2 = 'test2.hdf5'
CHANNEL_1 = 0
CHANNEL_2 = 1
EEG = 1
EEGA = 2

def example1():
    # Number of total samplepoints
    N = 800
    # Sample frequency
    f = 800
    # Sample spacing
    T = 1.0 / f

    t = np.linspace(0.0, N*T, N)
    # General sinus-function: y = sin(2*pi*f*t)
    y = 2.0 + sin(2.0*pi*50.0*t) + 0.5*sin(2.0*pi*80.0*t)
    y = signal.detrend(y)
    
    plt.plot(t, y)
    plt.grid()
    plt.show()

    xf = np.linspace(0.0, 1.0/(2.0*T), N/2)
    yf = abs(fft(y))

    plt.plot(xf, (2.0/N) * np.abs(yf[0:N/2]))
    plt.grid()
    plt.show()


def example2():
    freq = 100.0
    t = np.arange(0, 5, 0.01)
    y = 2*np.sin(2*np.pi*5*t) + np.sin(2*np.pi*20*t) + np.random.randn(t.size) 
    
    fig, ax = plt.subplots(1, 1, squeeze=True, figsize=(8, 3))
    ax.set_title('Time domain', fontsize=18)
    ax.plot(t, y, 'b', linewidth=2)
    ax.set_xlabel('t [s]')
    ax.set_ylabel('y')
    ax.locator_params(axis = 'both', nbins = 5)

    # frequency content
    N = y.size
    yfft  = fft(y, N)

    # let's take only the positive frequencies and normalize the amplitude
    yfft  = np.abs(yfft)/N
    freqs = fftfreq(N, 1./freq)
    freqs = freqs[:np.floor(N/2)]
    yfft  = yfft[:np.floor(N/2)]

    fig, ax = plt.subplots(1, 1, squeeze=True, figsize=(8, 3))
    ax.set_title('Frequency domain', fontsize=18)
    ax.plot(freqs, yfft, 'r',  linewidth=2)
    ax.set_xlabel('f [Hz]')
    ax.set_ylabel('FFT(y)')
    ax.locator_params(axis = 'both', nbins = 5)

    plt.tight_layout()
    plt.grid()
    plt.show()


def example3():
    reader = HDFReader();
    [mat, frequencies] = reader.read(TEST_FILE_2)
    data = np.asarray(mat[CHANNEL_1][EEGA]) # Get EEGA data from selected channel -> unfiltered data from headset

    # Number of total samplepoints
    N = data.size

    # Sample rate
    # NOTE: When f is obtained from the record (frequencies[EEGA]) this gives ~240 samples/s,
    #       which was calculated at writing the record, but the real fs is 256 samples/s 
    f = 256
    T = 1.0 / f # sample interval T = 1/256 = 0.0039 s
    
    x = np.linspace(0.0, (N*T), N)
    # OR: x = np.arange(0, N*T, T)
    y = signal.detrend(data)

    fig, ax = plt.subplots(1, 1, squeeze=True, figsize=(16, 5))
    mngr = plt.get_current_fig_manager()
    geom = mngr.window.geometry()
    left, top, width, height = geom.getRect()
    mngr.window.setGeometry(200, 30, width, height)

    ax.set_title('Time domain', fontsize=18)
    ax.plot(x, y, 'b', linewidth=2)
    ax.set_xlabel('t [s]')
    ax.set_ylabel('y')
    ax.locator_params(axis = 'both', nbins = 5)

    # frequency content
    yfft  = fft(y, N)

    # let's take only the positive frequencies and normalize the amplitude
    yfft  = np.abs(yfft) / N
    freqs = fftfreq(N, 1.0/f)
    freqs = freqs[0:np.floor(N/2)/2]
    yfft  = yfft[0:np.floor(N/2)/2]

    fig, ax = plt.subplots(1, 1, squeeze=True, figsize=(16, 4))
    mngr = plt.get_current_fig_manager()
    geom = mngr.window.geometry()
    left, top, width, height = geom.getRect()
    mngr.window.setGeometry(200, 520, width, height)

    ax.set_title('Frequency domain', fontsize=18)
    ax.plot(freqs, yfft, 'r',  linewidth=2)
    ax.set_xlabel('f [Hz]')
    ax.set_ylabel('FFT(y)')
    ax.locator_params(axis = 'both', nbins = 5)

    plt.tight_layout()
    plt.grid()
    plt.show()


if __name__ == '__main__':
    example2()