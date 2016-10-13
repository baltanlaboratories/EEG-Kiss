import unittest

from random import randint
from root.core.blackboardbuffer import BlackboardBuffer

class TestBlackboardBuffer(unittest.TestCase):

    test_pattern = "/test"

    def setUp(self):
        
        self.buffer = BlackboardBuffer(self.test_pattern)
        self.number_of_samples   = 1024
        self.vl                  = 10

    def put_random_data(self, number_of_samples=1):
        for _ in range( number_of_samples ):
            self.buffer.put_data( randint(0,1023) )

    def put_random_vectors(self, number_of_samples, vectorlength):
        for _ in range( number_of_samples ):
            self.buffer.put_data( [randint(0,1023) for _ in range(vectorlength) ] )

    def test_put_single( self ):  
        self.put_random_data(self.number_of_samples)
        self.assertEqual( self.buffer.get_count(), self.number_of_samples )       

    def test_put_multiple( self ):  
        self.put_random_vectors(self.number_of_samples,self.vl)
        self.assertEqual( self.buffer.get_count(), self.number_of_samples*self.vl )       

    def test_put_with_clear(self):       
        self.put_random_vectors(self.number_of_samples,self.vl)
        self.assertEqual( self.buffer.get_count(), self.number_of_samples*self.vl )   
        
        self.buffer.clear()
        self.assertEqual( self.buffer.get_count(), 0 )   
        
        self.put_random_vectors(2*self.number_of_samples,self.vl)
        self.assertEqual( self.buffer.get_count(), 2*self.number_of_samples*self.vl )     
        
    def test_get_pattern(self):
        self.assertEqual(self.buffer.get_pattern(), self.test_pattern)  
        
    def test_set_get_bufsize(self):
        bufsize = 20
        
        self.buffer.set_bufsize(bufsize)
        self.assertEqual(self.buffer.get_bufsize(), bufsize)
        
    def test_get_data_none(self):
        '''
           Retrieve data when no count is given 
        '''        
        buffer_data = self.buffer.get_data()
        
        # The buffer data contains 2 lists: data and timestamps
        self.assertEqual(len(buffer_data), 2)
        
        # Verify there is no data in both lists
        for data_set in buffer_data:
            self.assertEqual(len(buffer_data[data_set]), 0)

    def test_get_data_zero_count(self): 
        '''
           Retrieve data when a count of zero is given 
        '''         
        buffer_data_keys = ['data', 'timestamps']
        buffer_data      = self.buffer.get_data(0)
        
        # The buffer data contains 2 lists: data and timestamps
        self.assertEqual(len(buffer_data), 2)
        
        # Verify there is no data in both lists
        for k, v in buffer_data.iteritems():
            self.assertTrue(k in buffer_data_keys)
            self.assertEqual(len(v), 0)     
            
    def test_put_data_get_data(self):
        '''
           Retrieve data when a count of zero is given 
        '''         
        count_10 = 10
        
        # Fill the buffer with data
        self.put_random_data(self.number_of_samples)
        
        buffer_data = self.buffer.get_data(count_10)
        
        # The buffer data contains 2 lists: data and timestamps
        self.assertEqual(len(buffer_data), 2)        
        
        # The buffer data with the samples must be equal to the data that was set
        # I think this can be improved using a dictionary holding the values
        # This improves testability, now you assume data is always returned as first
        self.assertEqual(len(buffer_data['data']), count_10)         
        
        #buffer_data = self.buffer.get_data(self.number_of_samples)      
        #print len(buffer_data[0])
        #self.assertEqual(len(buffer_data[0]), self.number_of_samples) 
                 
    def test_get_last_timestamp_no_data(self):
        '''
            Verify the last timestamp of the initial buffer can be retrieved 
            (initially no timestamp shall be returned)
        '''
        self.assertEqual(self.buffer.get_last_timestamp(), 0)
        
    def test_get_last_timestamp_with_data(self):
        '''
            Verify the last timestamp of the buffer can be retrieved 
            (timestamp shall be None)
        '''      
        count_5 = 5
        
        # Fill the buffer with data
        self.put_random_data(count_5)     
        self.assertEqual(self.buffer.get_last_timestamp(), None)
        
    def test_get_timestamps_window_no_data(self):
        '''
            Verify a window of timestamps of the initial buffer can be retrieved 
            (shall return no timestamps)
        '''          
        result = self.buffer.get_timestamps_window(0, 1)
        self.assertEqual(len(result), 0)
        
    def _test_get_timestamps_window_with_data(self):
        '''
            Verify a window of timestamps of the initial buffer can be retrieved 
            (shall return None for all timestamps)
        '''              
        count_5 = 5
        
        # Fill the buffer with data
        self.put_random_data(count_5)
        
        result = self.buffer.get_timestamps_window(first=None, last=count_5-2)
        self.assertEqual(len(result), count_5-2)  
    
        for timestamp in result:
            self.assertEqual(timestamp, None)

if __name__ == '__main__':
    unittest.main()
