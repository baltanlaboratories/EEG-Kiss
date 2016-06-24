import unittest
from root.core.dataconsumer import DataConsumer
from root.core.blackboard import Blackboard
from root.input.datagenerator import DataGenerator
from time import sleep

class TestDataConsumer(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.blackboard = Blackboard()
        
        self.pat = '/test'
        self.gen = DataGenerator( self.blackboard, self.pat, [1], [1] )
        self.gen.start()
        self.pat2 = '/test2'
        self.gen2 = DataGenerator( self.blackboard, self.pat2, [2], [1] )
        self.gen2.start()

    def test_singel_data_stream(self):
        """
        Test whether data of single is coming through
        """
        DataConsumer( self.blackboard, self.pat )
        sleep( .5 )
        
        result = self.blackboard.get_data( self.pat )
        self.assertIsNotNone( result )
        self.assertGreater(len(result), 0 )

    def test_multiple_data_streams(self):
        DataConsumer( self.blackboard, [self.pat, self.pat2] )
        sleep( .5 )
        
        result = self.blackboard.get_data( self.pat )
        self.assertIsNotNone( result )
        self.assertGreater(len(result), 0 )
        
        result = self.blackboard.get_data( self.pat2 )
        self.assertIsNotNone( result )
        self.assertGreater(len(result), 0 )

        
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.gen.stop()
        self.gen2.stop()

if __name__ == '__main__':
    unittest.main()