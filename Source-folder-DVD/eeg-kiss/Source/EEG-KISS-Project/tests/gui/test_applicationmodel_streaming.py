'''
Created on 29 apr. 2015

@author: Bas.Kooiker
'''
import unittest
import mock

import time

from root.gui.applicationmodel import ApplicationModel
from root.input.datasimulator import DataSimulator

class TestApplicationModelStreaming( unittest.TestCase ):
    
    @mock.patch('serial.Serial')
    def _test_headset_1(self, serial_mock):
        """
        Test starting of streaming
        """
        model = ApplicationModel()
        model.select_port(0, "__test_port_name__")
        model.headsets[0].start()
        self.assertTrue(model.is_headset_streaming(), "Should be streaming from headset")
        model.headsets[0].stop()
        
    @mock.patch('serial.Serial')
    def _test_headset_2(self, serial_mock):
        """
        Test stopping of streaming
        """
        model = ApplicationModel()
        model.select_port(0, "__test_port_name__")
        model.headsets[0].start()
        model.stop_headsets()
        self.assertFalse(model.is_headset_streaming(), "Should not be streaming from headset")

    @mock.patch('serial.Serial')
    def _test_headset_3(self, serial_mock):
        """
        Test starting of toggle streaming
        """
        model = ApplicationModel()
        model.select_port(0, "__test_port_name__")
        model.start_headsets()
        time.sleep(.1)
        self.assertTrue(model.is_headset_streaming(), "Should be streaming from headset")
        model.stop_headsets()

    @mock.patch('serial.Serial')
    def _test_headset_4(self, serial_mock):
        """
        Test stopping of toggle streaming
        """
        model = ApplicationModel()
        model.select_port(0, "__test_port_name__")
        model.start_headsets()
        time.sleep(.1)
        model.stop_headsets()
        time.sleep(.1)
        self.assertFalse(model.is_headset_streaming(), "Should not be streaming from headset")

if __name__ == "__main__":
    unittest.main()
