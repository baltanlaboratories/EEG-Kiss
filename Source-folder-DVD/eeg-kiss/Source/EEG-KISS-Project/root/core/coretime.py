'''
Created on 6 mei 2015

@author: Bas.Kooiker
'''

from random import randint
import time

class CoreTime(object):
    
    class __CoreTime:
        def __init__(self):
            self._offset = time.clock()
        
        def __str__(self):
            return `self` + self._offset
        
        def reset(self):
            self._offset = time.clock()
                
        def now(self):
            return time.clock() - self._offset
        
    instance = None
    
    def __new__(cls): 
        if not CoreTime.instance:
            CoreTime.instance = CoreTime.__CoreTime()
        return CoreTime.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name):
        return setattr(self.instance, name)