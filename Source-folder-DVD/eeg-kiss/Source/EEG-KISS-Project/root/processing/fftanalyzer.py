'''
Created on Apr 3, 2015

@author: Sjors.Ruijgrok
'''

from root.core.dataconsumer import DataConsumer
from scipy.fftpack import fft
from scipy.fftpack import fftfreq
import numpy as np
from root.core.constants import PatternStrings, FrequencyBands

class FFTAnalyzer( DataConsumer ):
    """
    Implement DataConsumer to process incoming data with a sliding window 1/8 overlap and perform FFT.
    """

    def __init__(self, blackboard, patterns, freqbands=FrequencyBands.values, windowsize=512, samplerate=256):
        """
        @param blackboard:
            blackboard instance which contains the data that must be plotted.
        @param patterns
            the patterns corresponding to the data buffer that must be analyzed. 
        @param windowsize
            The size of the windows to perform FFT over
        @param samplerate
            Sample rate of the incoming data signal
        """
        if not isinstance( patterns, list ):
            patterns = [ patterns ]
            
        DataConsumer.__init__(self, blackboard, patterns)
        self.blackboard     = blackboard
        
        self.buffers        = { pat: [] for pat in patterns }
        self.bufs_alpha     = { pat: [] for pat in patterns }
        self.bufs_ts        = { pat: [] for pat in patterns }
        self._freqbands     = freqbands
        self._windowsize    = windowsize
        self._samplerate    = samplerate


    def _process_data(self, pattern, data, timestamps ):
        """
        Inherited from DataConsumer
        Adds incoming data to a data buffer
        If buffersize exceeds windowsize, FFT is performed and 1/8 of the buffer is removed to have overlapping windows.
        """
        self.buffers[pattern] = self.buffers[pattern] + data
        if len( self.buffers[pattern] ) > self._windowsize:
            freqs, fft = self._getFFT( self.buffers[pattern][:self._windowsize], self._samplerate )

            if not len(self._freqbands) == 0:
                # Fill buffers with average value for different frequency-bands and store these with latest received timestamp.
                # Also other calculations can be done here to get measures for arousal and valence.
                if FrequencyBands.DELTA in self._freqbands:
                    avg_delta = np.average([fft_value for freq, fft_value in zip(freqs, fft) if (0.5 <= freq < 4.0)])
                    self.blackboard.put_data( pattern + PatternStrings.DELTA, avg_delta, timestamps[-1] )
    
                if FrequencyBands.THETA in self._freqbands:
                    avg_theta = np.average([fft_value for freq, fft_value in zip(freqs, fft) if (4.0 <= freq < 8.0)])
                    self.blackboard.put_data( pattern + PatternStrings.THETA, avg_theta, timestamps[-1] )
    
                if FrequencyBands.ALPHA in self._freqbands:
                    avg_alpha = np.average([fft_value for freq, fft_value in zip(freqs, fft) if (8.0 <= freq < 14.0)])
                    self.blackboard.put_data( pattern + PatternStrings.ALPHA, avg_alpha, timestamps[-1] )
    
                if FrequencyBands.BETA in self._freqbands:
                    avg_beta  = np.average([fft_value for freq, fft_value in zip(freqs, fft) if (14.0 <= freq < 31.0)])
                    self.blackboard.put_data( pattern + PatternStrings.BETA, avg_beta, timestamps[-1] )
    
                if FrequencyBands.GAMMA in self._freqbands:
                    avg_gamma = np.average([fft_value for freq, fft_value in zip(freqs, fft) if (31.0 <= freq < 48.0)])  # Stay before 50 Hz
                    self.blackboard.put_data( pattern + PatternStrings.GAMMA, avg_gamma, timestamps[-1] )
            else:
                # Store FFT values
                self.blackboard.put_fft(pattern + PatternStrings.FFT, freqs.tolist(), fft)

            #print avg_alpha, zip(freqs, fft)
            
            # Keep latest values
            self.buffers[pattern] = self.buffers[pattern][self._windowsize/8:]


    def _getFFT(self, data, fs):
        """
        @param data: 
            set of samples
        @param fs  : 
            sample-rate of the data (samples/s)
        """
        # Number of total samplepoints
        N = len( data )
    
        # Sample rate 
        T = 1.0 / fs # sample interval T = 1/256 = 0.0039 s
        
        x = np.linspace(0.0, (N*T), N)
    
        # frequency content
        yfft  = fft(data, N)
    
        # let's take only the positive frequencies and normalize the amplitude
        yfft  = np.abs(yfft) / N
        freqs = fftfreq(N, T)
        half = int(np.floor(N/2)/2)
        freqs = freqs[0:half]
        yfft  = [yfft[0]] + [ y * 2 for y in yfft[1:half] ]
        
        return freqs, yfft


    def setFreqBands(self, freqbands):
        self._freqbands = freqbands
    
    def setPatterns(self, patterns):
        self._patterns = patterns
        
    def resetBuffers(self):
        self.buffers        = { pat: [] for pat in self._patterns }
        self.bufs_alpha     = { pat: [] for pat in self._patterns }
        self.bufs_ts        = { pat: [] for pat in self._patterns }
