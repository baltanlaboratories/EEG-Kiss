import unittest
from root.core.processingthread import ProcessingThread
from time import sleep

class SimpleProcessingThread( ProcessingThread ):
    
    def __init__(self):
        ProcessingThread.__init__( self )
        self.called = False
    
    def process_step(self):
        self.called = True

class TestProcessingThread(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.tearDown(self)
        self.pt = SimpleProcessingThread()
        self.assertFalse( self.pt._running )
        self.pt.start()
        sleep(.1)
        self.assertTrue( self.pt._running )
        self.pt.stop()
        
    
    def test_threading_state( self ):
        self.assertFalse( self.pt._running )
    
    def test_called( self ):
        self.assertTrue( self.pt.called )

    def tearDown(self):
        unittest.TestCase.tearDown(self)

if __name__ == '__main__':
    unittest.main()