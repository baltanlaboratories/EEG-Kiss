'''
Created on 29 apr. 2015

@author: Bas.Kooiker
'''
import unittest
import Tkinter as tk

from root.gui.applicationmodel import ApplicationModel
from root.input.datasimulator import DataSimulator

class TestApplicationModel( unittest.TestCase ):
    
    def setUp(self):
        self.root = tk.Tk('EEG kiss')
    
    #@patch('root.core.settings.TimeSettings')
    def test_init(self):
        """
        Tests for initial state
        """
        model = ApplicationModel()
        
        self.assertEqual(model.get_simulation_state(), DataSimulator.IDLE, "Simulation state should initialize as IDLE")
        self.assertFalse(model.is_receiving_data(), "Should not be receiving data")
        self.assertFalse(model.is_recording(), "Should not be recording data")
        self.assertFalse(model.is_headset_streaming(), "Should not be streaming from headset")
        self.assertFalse(model.is_headset_connected(), "No headset should be selected")
        
if __name__ == "__main__":
    unittest.main()
