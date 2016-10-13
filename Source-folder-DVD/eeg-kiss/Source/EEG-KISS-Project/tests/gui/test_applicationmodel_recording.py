'''
Created on 29 apr. 2015

@author: Bas.Kooiker
'''
import unittest

import Tkinter as tk

from root.gui.applicationmodel  import ApplicationModel

class TestApplicationModelRecording( unittest.TestCase ):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self._tk = tk.Tk()
        
    def test_headset_1(self):
        """
        Test recording state after streaming start
        """
        model = ApplicationModel()
        model.start_headsets()
        self.assertFalse(model.is_recording(), "Should not be recording")
        model.stop_headsets()
    
    def test_headset_2(self):
        """
        Test recording state after streaming start and setting of filename
        """
        model = ApplicationModel()
        model.start_headsets()
        self.assertFalse(model.is_recording(), "Should not be recording")
        model.stop_headsets()

    def test_headset_3(self):
        """
        Test recording state after streaming start
        """
        record_time = 10
        
        model = ApplicationModel()
        model.start_headsets()
        model.start_recording(record_time)
        self.assertTrue(model.is_recording(), "Should be recording")
        model.stop_recording()
        model.stop_headsets()
        
    def test_headset_4(self):
        """
        Test recording state after streaming start
        """
        record_time = 10
        
        model = ApplicationModel()
        model.start_headsets()
        model.start_recording(record_time)
        model.stop_recording()
        model.stop_headsets()
        self.assertFalse(model.is_recording(), "Should not be recording")
        
if __name__ == "__main__":
    unittest.main()
