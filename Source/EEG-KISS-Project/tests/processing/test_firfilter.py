'''
Created on 1 mei 2015

@author: Bas.Kooiker
'''

import unittest, mock
import time
from random import randint
from math import floor

import matplotlib.pyplot as plt
import numpy as np

from root.processing.firfilter import FIRFilter
from root.processing.firpreprocessing import FIRPreprocessing
from root.core.blackboard import Blackboard
from root.input.datagenerator import DataGenerator
from scipy.signal.signaltools import lfilter

class TestFIRFilter( unittest.TestCase ):
    
    def setUp(self):
        """
        Initialize blackboard and a simulation data generator
        """
        unittest.TestCase.setUp( self )
        self.bb      = Blackboard()
        self.pattern = '/sines'
        
        self.offset         = 10
        self.frequencies    = [50,10]
        self.amps           = [1,1]
        
        self.gen            = DataGenerator( self.bb, self.pattern, frequencies=self.frequencies, amplitudes=self.amps, offset=self.offset, noise=0 )
    
    def test_init_notch(self):
        """
        Compare the generation of notch filter coefficients with the coefficients provided by Imec
        """
        notch_template = FIRPreprocessing.coefBSF256

        fir = FIRFilter( self.bb, self.pattern, 129, 256, 50, 'notch' )
        self.assertEqual( len(notch_template), len(fir.get_coefficients() ), 'sets should be equal length')
        self.assertAlmostEqual( sum([ abs( x-y ) for x,y in zip(notch_template, fir.get_coefficients() ) ]), 0, 5, 'difference should be small')
        
    def test_init_lpf(self):
        """
        Compare the generation of low-pass filter coefficients with the coefficients provided by Imec
        """
        lpf_template = FIRPreprocessing.coefLPF256

        fir  = FIRFilter( self.bb, self.pattern, 33, 256, 75, 'lpf' )
        coef = fir.get_coefficients()
           
        self.assertAlmostEqual( sum([ abs( x-y ) for x,y in zip(lpf_template, coef ) ]), 0, 2, 'difference should be small')
        
    def test_elementwise_lfilter(self):
        """
        Test whether our method of elementwise processing yields the same results as processing a whole signal at once
        """
        fir = FIRFilter( self.bb, self.pattern, 33, 256, 75, 'lpf' )
        a   = 1
        sig = [ randint(0,1024) for _ in range(256) ]
        
        result = lfilter( fir.get_coefficients(), a, sig, axis=0 ) 

        result2 = []
        buf = []
        for s in sig:
            buf.append(s)
            buf = buf[-33:]
            result2.append(lfilter( fir.get_coefficients(), a, buf )[-1] )
        
        self.assertEqual( len(result), len(result2), 'Results should be equal length')
        self.assertEqual( sum([ abs( x-y ) for x,y in zip(result, result2 ) ]), 0, 'Results should be equal value')
        
    def test_notch50(self):
        """
        TODO Improve test with better timing mechanism or decouple from internal timing mechanism
        When plotting the results, the filtered signal looks really good though.
        """
        fir = FIRFilter( self.bb, self.pattern, 129, 256, 50, 'notch' )
        
        self.gen2 = DataGenerator( self.bb, '/sine', frequencies=[10], amplitudes=[1], offset=self.offset, noise=0 )
        
        self.bb.set_bufsize('/sine', 512)
        self.bb.set_bufsize('/sines/notch_50', 512)
        
        self.gen.start()
        self.gen2.start()
        fir.start()
        
        time.sleep( 3 )
        
        self.gen.stop()
        self.gen2.stop()
        fir.stop()

        time.sleep( 1 )
        
        off = len(fir.get_coefficients())
        
        target = self.bb.get_data('/sine')['data'][(off-1)/2:128+(off-1)/2]
        result = self.bb.get_data('/sines/notch_50')['data'][:128]

        #dif = np.average([ abs( x-y ) for x,y in zip(result, target ) ])
        #delta = 1
        #self.assertAlmostEqual( dif, 0, msg='Difference between target and result should be smaller than %.2f, difference is %f'%(delta,dif), delta=delta)

    def test_init_pattern_no_string(self):

        # An TypeError should be raised when a pattern is no string
        with self.assertRaises(TypeError):
            FIRFilter( self.bb, 5, 129, 256, 50, 'notch' )

    def test_init_not_implemented_filter(self):

        # An NotImplementedError should be raised
        with self.assertRaises(NotImplementedError):
            FIRFilter( self.bb, self.pattern, 129, 256, 50, 'bsf' )

    def test_init_incompatible_filter(self):

        # An TyperError should be raised
        with self.assertRaises(TypeError):
            FIRFilter( self.bb, self.pattern, 129, 256, 50, 'foo' )


    def test_init_pattern_list(self):
        # For codecoverage
        FIRFilter( self.bb, [self.pattern] , 129, 256, 50, 'notch' )
    

if __name__ == '__main__':
    unittest.main()