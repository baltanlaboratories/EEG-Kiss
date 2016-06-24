'''
Created on 29 apr. 2015

@author: Bas.Kooiker
'''
import unittest
import mock

import numpy as np

from root.gui.applicationmodel import ApplicationModel
from root.input.datasimulator import DataSimulator
from root.input.hdfreader import HDFReader
from time import sleep
from tests.input import filenames


class TestApplicationModelSimulation( unittest.TestCase ):

    def setUp(self):
        unittest.TestCase.setUp(self)
        
        self.model = ApplicationModel()
        
        _eeg_type = 1
        
        [ mat, frequencies ] = HDFReader().read( filenames[6][0] )
        data = [ np.asarray( mat[i-1][ _eeg_type ] ) for i in range(1,9) ]  
        
        interval = 1. / frequencies[_eeg_type]  
        
        self.model.simulators[0].set_simulation_data(data)
        self.model.simulators[0].set_simulation_interval(interval)
        
        eeg_chans = ['/eega0/channel_%d/pp' % i for i in range(1,9) ]
        
        self.model.simulators[0].set_patterns( eeg_chans )
    
    def _test_modelstate_1(self):
        self.model.start_simulation()
        self.assertEquals( self.model.get_simulation_state(), DataSimulator.PLAYING )
        self.model.stop_simulation()
        
    def _test_modelstate_2(self):
        self.model.start_simulation()
        self.model.stop_simulation()
        self.assertEquals( self.model.get_simulation_state(), DataSimulator.IDLE )
         
    def _test_modelstate_3(self):
        self.model.start_simulation()
        self.model.pause_simulation()
        sleep( .2 )
        self.assertEquals( self.model.get_simulation_state(), DataSimulator.PAUSED )
        self.model.stop_simulation()
         
    def _test_modelstate_4(self):
        self.model.pause_simulation()
        self.assertEquals( self.model.get_simulation_state(), DataSimulator.IDLE )
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.model.stop_simulation()
        self.model.stop_recording()
        self.model.stop_headsets()
        
if __name__ == "__main__":
    unittest.main()
