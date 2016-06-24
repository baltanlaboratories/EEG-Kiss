import unittest 

from matplotlib                         import pyplot

from random                             import randint

from root.input.imecinput               import ImecInput
from root.core.blackboard               import Blackboard
from root.input.datagenerator           import DataGenerator
from root.processing.iirlowpassfilter   import IIRLowPassFilter
from root.processing.iirnotchfilter     import IIRNotchFilter
from root.input.hdfreader               import HDFReader
from root.processing.firpreprocessing   import FIRPreprocessing

from tests.input                        import filenames

from time                               import sleep

class TestFirPreprocessing(unittest.TestCase):

    def setUp(self):        
        self.bb         = Blackboard()
        self.input      = HDFReader()
    
    def create_filters(self): 
        # create preprocessing filters
        self._processors = []
        
        self.headset = 0
        self.channel = 1
        
        notch   = 50
        lowpass = 80
        
        filter_pattern1 = '/lpf%d' % ( lowpass )
        filter_pattern2 = '/notch%d' % ( notch )
        
        self.pat = '/eeg%d/channel_%d' % ( self.headset, self.channel )
        lp = IIRLowPassFilter( self.bb, [self.pat], lowpass=lowpass )
        self._processors.append( lp )
        self.pat_lpf = self.pat + filter_pattern1
        
        nf = IIRNotchFilter( self.bb, [self.pat_lpf], cutoff_freq = notch, cutoff_width=1 )
        self._processors.append( nf )
        self.pat_notch = self.pat_lpf + filter_pattern2
        
        nf = IIRNotchFilter( self.bb, [self.pat], cutoff_freq = notch, cutoff_width=1 )
        self._processors.append( nf )
        self.pat_notch1 = self.pat + filter_pattern2
        
        pp = FIRPreprocessing( self.bb, [self.pat] )
        self._processors.append( pp )
        self.pat_pp     = self.pat + '/pp'
        
    def test_start(self):
        self.create_filters()
                
        offset         = 5000
        plot_size      = 1000
        offset         = 5000
        last_count      = 0
        result         = []
        frequencies    = [1,3,5,7]
        amps           = [1,2,1,8]
        
        gen            = DataGenerator( self.bb, self.pat, frequencies=frequencies, amplitudes=amps, offset=offset, noise=0 )

        self.bb.set_bufsize( self.pat_pp, 128 )
        
        gen.start()        

        # Start filters
        for p in self._processors:
            p.start() 
        
        sleep(1)
        
        # Start processing data
        #for d in self.original[:]:
        #    self.bb.put_data( self.pat, d )
        #    local_count = self.bb.get_count( self.pat )
        #    dif = local_count - last_count
        #    if dif > 0:
        #        last_count = local_count
        #        local_results = self.bb.get_data( self.pat_pp )['data']
        #        if local_results:
        #            local_results = local_results[-dif:]
        #            for r in local_results:
        #                result.append(r)
        #    sleep(.00001)
    
        sleep(3)
        
        # Stop filters
        for p in self._processors:
            p.stop()  

        gen.stop()  
        
    def test_init_firpreprocessing_pattern_no_string(self):

        with self.assertRaises(TypeError):
            FIRPreprocessing( self.bb, 2 )

    def tearDown(self):
        unittest.TestCase.tearDown(self)

if __name__ == '__main__':
    unittest.main()
