import unittest

from root.core.ordinarybuffer import OrdinaryBuffer

class OrdinaryBufferTest(unittest.TestCase):
    
    test_pattern = "/test"
    
    def setUp(self):
        self.ordindary_buffer = OrdinaryBuffer(self.test_pattern)
    
    def test_put_data_no_list(self):
        '''
            Put data in the buffer for code coverage
        '''      
        self.ordindary_buffer.put_data(10, 5)
    
    def test_put_data_list_get_count(self):
        '''
            Put lists of data in the buffer for code coverage afterwards 
            verify if the count of the x-axis is retrieved correctly
        '''
        xaxis = list(range(0, 10))
        yaxis = list(range(0,5))
        
        self.ordindary_buffer.put_data(xaxis, yaxis)
        
        self.assertEqual(self.ordindary_buffer.get_count(), len(xaxis))
        
    def test_put_data_list_get_axis(self):
        '''
            Put lists of data in the buffer for code coverage 
            and verify if the axis have been set for both axis
        '''        
        xaxis = list(range(0, 10))
        yaxis = list(range(0,5))
        
        self.ordindary_buffer.put_data(xaxis, yaxis)
        
        self.assertEqual(self.ordindary_buffer.get_xaxes(), xaxis)
        self.assertEqual(self.ordindary_buffer.get_yaxes(), yaxis)
        
    def test_get_pattern(self):
        '''
            Verify if the pattern is retrieved correctly
        '''
        self.assertEqual(self.ordindary_buffer.get_pattern(), self.test_pattern)        
        
        
    def test_get_count(self):
        '''
            Verify if the count of the x-axis is retrieved correctly
        '''
        self.assertEqual(self.ordindary_buffer.get_pattern(), self.test_pattern)        
        
                   
if __name__ == '__main__':
    unittest.main()    