'''
Created on Mar 5, 2015

@author: Sjors.Ruijgrok
'''

import unittest

import os

from root.input.hdfreader import HDFReader 
from numpy import float32, float64

#  This TestCase checks the read-function of HDFReader
class TestHDFReader(unittest.TestCase):

    _file_string1 = os.path.dirname(__file__) + '/testfile_no_HDF5.h5'
    _file_string2 = os.path.dirname(__file__) + '/testfile_fixedvalues.h5'

    def setUp(self):
        unittest.TestCase.tearDown(self)
        # Initialize data reader
        self._reader = HDFReader();


    def tearDown(self):
        unittest.TestCase.tearDown(self)


    def test_read_noHDF5File(self):
        # Open a test-file that is not in HDF5 format and check if error is raised
        self.assertRaisesRegexp(TypeError, "File is not a HDF5 file", self._reader.read, (self._file_string1))


    def test_read_HDF5FixedValues(self):
        channelCount = 8
        dataCount = 10
        fixedData = 1.0
        channelType = 1 # These are the EEG channels -> only this data is checked
        
        # Open a test-file that is in HDF5 format for checking returned values
        [ mat, frequencies, _ ] = self._reader.read(self._file_string2)
        
        # Check data matrix (3-dimensional: 1st index = channel, 2nd index = type, 3rd index = data)
        for i in range(0, channelCount):
            for j in range(0, dataCount):
                matData = mat[i][channelType][j]
                self.assertEqual(matData, float32(fixedData))
                fixedData += 0.1
           
        # Check frequencie (read from EEG-1 channel)
        self.assertEqual(frequencies[channelType], 123456789)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
