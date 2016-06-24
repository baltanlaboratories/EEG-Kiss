'''
Created on 6 mei 2015

@author: Bas.Kooiker
'''

import unittest, mock
import time

from root.core.coretime import CoreTime

class TestCoreTime( unittest.TestCase ):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        
    def test_singleton(self):
        t1 = CoreTime()
        t1.reset()
        moment_1 = t1.now()
        
        off1 = t1._offset
        
        time.sleep( 1 )
        
        t2 = CoreTime()
        t2.reset()
        moment_2 = t2.now()
        
        off2 = t2._offset
        
        self.assertEqual(t1, t2, msg="instances are not equal")
        self.assertAlmostEqual(moment_1, moment_2, msg="moments should be about equal", delta=.001)
        self.assertNotEqual(off1, off2, msg="values are not equal %d %d"%(off1,off2))
        
    def _test_stopwatch(self):
        ct = CoreTime()
        ct.reset()
        
        samples = 10
        times = []
        for i in range(samples):
            times.append( ct.now() )
            time.sleep(1)
            
        for i in range(samples-1):
            self.assertAlmostEqual(times[i], times[i+1]-1, msg='Difference should be about 1. Difference is %f'%(times[i] - times[i+1] + 1), delta=.02)
