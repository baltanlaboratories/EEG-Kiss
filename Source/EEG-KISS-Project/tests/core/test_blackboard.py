import unittest

from random import randint

from root.core.blackboard import Blackboard 

# test constants
test_pattern            = '/test/whatev'
test_pattern_2          = '/test/whatever_again'
test_value              = 42
test_buffersize         = 1024
number_of_test_samples  = 24

class TestBlackboard(unittest.TestCase):

    def setUp(self):
        self.blackboard = Blackboard()

    """ Test put functionality  """
    def test_put(self):
        # put value in buffer
        self.blackboard.put_data( test_pattern, test_value )
        
        # buffer should only contain the added value in a list
        self.assertEquals( self.blackboard.get_data(test_pattern)['data'], [test_value] )   
        
        # set buffersize and add a lot of data
        for pat in self.blackboard.get_patterns():
            self.blackboard.set_bufsize( pat, test_buffersize )
        for _ in range( 2000 ):
            self.blackboard.put_data( test_pattern, randint( 0, 256 ) )
            
        # check whether buffer size remains within buffersize
        self.assertEqual( len( self.blackboard.get_data( test_pattern )['data'] ), test_buffersize )
        
    """ Test get functionality """
    def test_get(self):
        # register buffer, set buffersize and add a bit of data
        for pat in self.blackboard.get_patterns():
            self.blackboard.set_bufferlength( test_buffersize )
        for _ in range( number_of_test_samples ):
            self.blackboard.put_data( test_pattern, randint( 0, 256 ) )
            
        # buffer should contain the number of added samples
        self.assertEquals( len( self.blackboard.get_data( test_pattern )['data'] ), number_of_test_samples)        
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)

if __name__ == '__main__':
    unittest.main()
