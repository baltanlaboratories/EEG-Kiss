from time import clock
import numpy as np
from random import random
from math import sin

from root.core.processingthread import ProcessingThread


class DataGenerator( ProcessingThread ):
    
    def __init__( self, blackboard, pattern, frequencies=[], amplitudes=[], noise=0, offset=0, Fs=256 ):
        
        if len(frequencies) != len(amplitudes):
            raise TypeError( 'number of frequencies and amplitudes should be equal' )
        
        ProcessingThread.__init__( self )
        
        self.blackboard    = blackboard
        self._pattern       = pattern
        self._frequencies   = frequencies
        self._amplitudes    = amplitudes
        self._noise         = noise
        self._offset        = offset
        self._Fs            = Fs
        
        self._start_time        = clock()
        self._processed_samples = 0
    
    def process_step(self):
        """
        Inherited from ProcessingThread
        """
        now                 = clock()
        dif                 = now - self._start_time 
        total_nr_samples    = int(dif * self._Fs )
        for i in range( self._processed_samples, total_nr_samples ):
#             y       = sum([ amp*np.sin(2*np.pi*freq*i) for freq, amp in zip(self._frequencies, self._amplitudes) ])
            y       = 0
            for freq, amp in zip(self._frequencies, self._amplitudes):
                y += amp * np.sin( 2*np.pi*freq*i / self._Fs )  
            n       = 2*self._noise*random() - self._noise
            value   = y + n + self._offset
            self.blackboard.put_data( self._pattern, value ) 
            
        self._processed_samples = total_nr_samples
            
    
    def start(self):
        """
        Overrides ProcessingThread
        """
        if not self._running:
            self._start_time = clock()
        ProcessingThread.start( self )
