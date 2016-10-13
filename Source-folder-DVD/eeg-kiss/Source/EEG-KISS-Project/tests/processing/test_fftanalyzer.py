import unittest

from matplotlib import pyplot as plt
from time       import sleep

from root.processing.fftanalyzer import FFTAnalyzer
from root.core.blackboard        import Blackboard
from root.input.datagenerator    import DataGenerator

class TestFreqSpectrum(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.bb = Blackboard()
        pattern = '/sines'
        
        self.offset         = 10
        self.frequencies    = [1,3,5,7]
        self.amps           = [1,2,1,8]
        
        self.gen            = DataGenerator( self.bb, pattern, frequencies=self.frequencies, amplitudes=self.amps, offset=self.offset, noise=0 )
        self.freqspec       = FFTAnalyzer( self.bb, pattern, windowsize=256 )
        self.bb.set_bufsize( '/sines/fft', 128 )

    def test_fft(self):
        self.gen.start()
        self.freqspec.start()
        
        sleep( 3 )
        
        self.gen.stop()
        self.freqspec.stop()

        result = self.bb.get_data('/sines/fft')
        
        # Enable when code coverage is guaranteed
        #self.assertAlmostEqual( result['data'], self.offset, msg="Offset difference too big", delta=.15 )
        
        #for f,amp in zip(self.frequencies,self.amps):
        #    self.assertAlmostEqual( result[f], amp, msg="Power difference too big: freq %f - original %f - measured %f" % (f, amp, result[f]), delta=.15 )
        
    def test_setFreqBands(self):
        '''
            Verify if frequency bands can be set
            For now only call the function for code coverage
        '''
        test_freq = 10

        self.freqspec.setFreqBands(test_freq)


    def test_setPatterns(self):
        '''
            Verify if patterns can be set
            For now only call the function for code coverage
        '''
        test_pattern = '/test'

        self.freqspec.setPatterns(test_pattern)

    def test_resetBuffers(self):
        '''
            Verify if buffers can be reset
            For now only call the function for code coverage
        '''
        self.freqspec.resetBuffers()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

if __name__ == '__main__':
    unittest.main()
