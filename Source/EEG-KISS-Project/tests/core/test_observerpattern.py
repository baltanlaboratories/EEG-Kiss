'''
Created on 24 apr. 2015

@author: Bas.Kooiker
'''
import unittest

from root.core.observerpattern import Observer, Subject

class SimpleObserver( Observer ):
    
    def __init__(self):
        self._notified = False
        
    def notify(self,message=None):
        self._notified = True

class TestObserverPattern(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.ob1 = Observer()
        self.ob2 = Observer()
        self.ob3 = Observer()
        self.sub = Subject()

    def test_registration(self):
        """
        Test for adding and removing observers
        """
        self.assertEqual(len(self.sub._observers),0,"Length should be 0")
        self.sub.register_observer(self.ob1)
        self.assertEqual(len(self.sub._observers),1,"Length should be 1")
        self.sub.register_observer(self.ob1)
        self.assertEqual(len(self.sub._observers),1,"Length should be 1")
        self.sub.register_observer(self.ob2)
        self.assertEqual(len(self.sub._observers),2,"Length should be 2")
        
        self.sub.unregister_observer(self.ob3)
        self.assertEqual(len(self.sub._observers),2,"Length should be 2")
        self.sub.unregister_observer(self.ob2)
        self.assertEqual(len(self.sub._observers),1,"Length should be 1")
        self.sub.unregister_observer(self.ob1)
        self.assertEqual(len(self.sub._observers),0,"Length should be 0")
        
    def test_abstract_notification(self):
        """
        Test whether error is raised when abstract notify method is called
        """
        self.sub.register_observer(self.ob1)
        self.sub.register_observer(self.ob2)
        self.assertRaises(NotImplementedError, self.sub.notify_observers )
        
    def _test_concrete_notification(self):
        """
        Test whether notify is called in concrete observer
        """
        self.ob1 = SimpleObserver()
        self.ob2 = SimpleObserver()
        self.sub.register_observer(self.ob1)
        self.sub.register_observer(self.ob2)
        self.assertFalse( self.ob1._notified )
        self.assertFalse( self.ob2._notified )
        self.sub.notify_observers()
        self.assertTrue( self.ob1._notified )
        self.assertTrue( self.ob2._notified )
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)

if __name__ == '__main__':
    unittest.main()
