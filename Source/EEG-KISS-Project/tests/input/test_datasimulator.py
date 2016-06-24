'''
Created on 29 apr. 2015

@author: Bas.Kooiker
'''

import unittest
import random

import numpy as np

from root.input.datasimulator   import DataSimulator
from root.core.blackboard       import Blackboard
from root.input.hdfreader       import HDFReader
from tests.input                import filenames

import time

class TestDataSimulator(unittest.TestCase):
    
    def setUp(self):
        # This can possibly be improved for testability!!
        # The datatypes must be defined somewhere globally       
        self.states = {'IDLE': 1, 'PAUSED': 2, 'PLAYING': 3}
    
    def _test_set_data_and_playback_states(self):
        bb = Blackboard()
        sim = DataSimulator( bb )
        
        reader = HDFReader();
         
        filename = filenames[5][0]
         
        # Reading two datafiles
        [ mat, frequencies, _ ] = reader.read(filename)       # Read data from first data file
        data = [ np.asarray( mat[i-1][ 1 ] ) for i in range(1,9) ]       # get data from selected channels
        patterns = ['/EEG/channel_%d' % (i) for i in range(1,9) ]
        
        interval = 1. / frequencies[ 1 ]  
        
        sim.set_simulation_data(data)
        sim.set_simulation_interval(interval)
        sim.set_patterns(patterns)
        
        self.assertEqual(sim.get_simulation_state(), DataSimulator.IDLE, "Simulator should be idle now")
        sim.start()
        time.sleep(.1)
        self.assertEqual(sim.get_simulation_state(), DataSimulator.PLAYING, "Simulator should be playing now")
        sim.pause()
        time.sleep(.1)
        self.assertEqual(sim.get_simulation_state(), DataSimulator.PAUSED, "Simulator should be paused now")
        sim.start()
        time.sleep(.1)
        self.assertEqual(sim.get_simulation_state(), DataSimulator.PLAYING, "Simulator should be playing now")
        sim.stop()
        time.sleep(.1)
        self.assertEqual(sim.get_simulation_state(), DataSimulator.IDLE, "Simulator should be stopped now")
    
        self.assertTrue(bb.get_count(patterns[0]) > 0, "Samples should be received on blackboard")
     
     
     
    def _test_get_time(self):
        bb = Blackboard()
        sim = DataSimulator( bb )
        
        reader = HDFReader();
         
        filename = filenames[5][0]
         
        # Reading two datafiles
        [ mat, frequencies, _ ] = reader.read(filename)       # Read data from first data file
        data = [ np.asarray( mat[i-1][ 1 ] ) for i in range(1,9) ]       # get data from selected channels
        patterns = ['/EEG/channel_%d' % (i) for i in range(1,9) ]
        
        interval = 1. / frequencies[ 1 ]  
        
        sim.set_simulation_data(data)
        sim.set_simulation_interval(interval)
        sim.set_patterns(patterns)
        
        total_time = sim.get_total_time()
        
        start_time = sim.get_current_time()
        self.assertEquals(start_time, 0, 'Time should be zero before playback')
        
        sim.start()
        
        time.sleep( 3 )
        
        now_time = sim.get_current_time()
        self.assertAlmostEquals(now_time, 3, msg='Time should be close to 3 after 3 seconds playback. Is %f'%now_time, delta=.05)
     
        sim.set_time( total_time - 2 )
        self.assertTrue( sim.get_simulation_state() is DataSimulator.PLAYING, 'Should be playing after setting time')
        
        time.sleep(3)
        
        self.assertTrue( sim.get_simulation_state() is DataSimulator.IDLE, 'Should be done playing')
        
        sim.stop()
    
    def test_set_simulation_data(self):
        ''' 
            Verify if the simulation data can be set 
            Only function is called to improve (functional) code coverage, so no verification yet
        '''    
        blackboard = Blackboard()
        simulator  = DataSimulator( blackboard )    
        sim_data   = self.create_simulation_data()
        
        simulator.set_simulation_data(sim_data)
        
    def test_get_set_simulation_state(self):
        ''' 
            Verify if the getting and setting of simulation states works correctly
        '''                  
        blackboard = Blackboard()
        simulator  = DataSimulator( blackboard )   
        
        # Set all the states and verify if the state is set correctly
        for _, value in self.states.iteritems():           
            simulator.set_state(value)
            self.assertEqual(simulator.get_simulation_state(), value)
      
    def test_reset(self):
        '''
            Call the reset function to improve (functional) code coverage
        '''
        blackboard = Blackboard()
        simulator  = DataSimulator( blackboard )       
      
        simulator.reset()
        
    def test_pause(self):
        '''
            Call the pause function to improve (functional) code coverage
        '''
        blackboard = Blackboard()
        simulator  = DataSimulator( blackboard )     
        
        simulator.set_state(self.states.get('PLAYING'))
        simulator.pause()
        self.assertEqual(simulator.get_simulation_state(), self.states.get('PAUSED'))
     
    def test_play_stop(self):
        blackboard = Blackboard()
        simulator  = DataSimulator( blackboard )             
        
        # Prepare the simulator preconditions
        simulator.set_simulation_data("test")
        simulator.set_patterns("test")
        simulator.set_simulation_interval(1)
        
        simulator.start()
        simulator.stop()
        
        simulator.set_state(self.states.get('PAUSED'))
        simulator.start()
        simulator.stop()
             
                
    def create_simulation_data(self):
        '''
            Helper function to initiate data matrix
            3-dimensional list for:
                8 channels of the eeg headset
                6 types of data
                unknown number of samples
        '''       
        mat   = [[[] for _ in range(6)] for _ in range(8)]
        types = ['DC', 'EEG', 'EEGA', 'ImpI', 'ImpIQ', 'ImpQ']

        for i in range(1, 9):
            for index, _ in enumerate(types):
                mat[i - 1][index] = np.float64(random.randint(2000, 2500))        
                
        return [ np.asarray( mat[i-1][ 1 ] ) for i in range(1,9) ] 
    
    def test_get_total_time(self):
        '''
            Call the get_total_time function to improve (functional) code coverage
        '''        
        blackboard = Blackboard()
        simulator  = DataSimulator( blackboard )  
        
        self.assertEqual(simulator.get_total_time(), -1)
        
        #simulator.set_patterns("test")
        #simulator.set_simulation_interval(1)
        
        #nr_of_samples = 5
        
        #simulator.set_simulation_data([0 for _ in xrange(nr_of_samples)])
        #self.assertEqual(simulator.get_total_time(), 0)
                
    def test_get_current_time(self):
        '''
            Call the get_current_time function to improve (functional) code coverage
        '''                       
        blackboard = Blackboard()
        simulator  = DataSimulator( blackboard )  

        self.assertEqual(simulator.get_current_time(), -1)
                         
    def test_set_time(self):
        '''
            Call the set_time function to improve (functional) code coverage
        '''         
        blackboard = Blackboard()
        simulator  = DataSimulator( blackboard )  
                   
        simulator.set_time(5)
        
        
                           
if __name__ == '__main__':
    unittest.main()
