'''
Created on 18 mei 2015

@author: Bas.Kooiker
'''

import unittest, mock
import os
import time

import numpy as np

from root.input.timedsimulator import TimedSimulator
from root.core.blackboard import Blackboard
from root.input.hdfreader import HDFReader
import root.core.coretime

test_filename = os.path.dirname(__file__) + '/testfile_timestamps.h5'

class TestTimedSimulator( unittest.TestCase ):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.bb = Blackboard()
        self.sim = TimedSimulator( self.bb )
        
        [ mat, _ ] = HDFReader().read( test_filename )       # Read data from first data file
        _data = []
        for i in range(4):
            _data.append( [ v[:2] for v in mat[i][ 1 ] ] )
        self.sim.set_simulation_data( _data )

        eeg_chans = ['/EEG_0/channel_%d/notch_50/lpf_75' % (i+1) for i in range(4) ]
        
        self.sim.set_patterns( eeg_chans )
           
    def _test_set_simulation_data(self):
        """
        Integrated test with Blackboard
        """
        self.assertTrue( len( self.sim._samples ) > 0, "Samples are not set correctly")
        self.assertTrue( np.shape( self.sim._timestamps ) == np.shape( self.sim._samples ), "Timestamps and samples do not have same length")
        
#     @mock.patch('root.core.coretime.CoreTime')
#     def test_process_step(self, time_mock):
#         nr = 5
#         for i in range( nr ):
#             time_mock.instance.now.return_value = i
#             self.sim._state = TimedSimulator.PLAYING
#             self.sim.process_step()
        
    @mock.patch('root.core.coretime.CoreTime')
    def _test_process_step_2(self, time_mock):
        nr = 10
        self.sim._state = TimedSimulator.PLAYING
        for i in range( nr ):
            time_mock.instance.now.return_value = i
            self.sim._state = TimedSimulator.PLAYING
            self.sim.process_step()
        
