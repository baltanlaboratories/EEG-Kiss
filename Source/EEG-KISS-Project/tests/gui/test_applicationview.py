'''
Created on 29 apr. 2015

@author: Bas.Kooiker
'''

import unittest
from root.gui.applicationview import ApplicationView

class TestApplicationView(unittest.TestCase):
    
    def test_initiaization(self):
        '''
            Application view init for code coverage
        '''
        view = ApplicationView()
    
if __name__ == '__main__':
    unittest.main()    
