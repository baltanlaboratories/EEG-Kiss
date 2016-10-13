'''
Created on 24 apr. 2015

@author: Bas.Kooiker
'''

class Observer():
    
    def notify(self,message=None, arg=None):
        raise NotImplementedError()
    
class Subject():
    
    def __init__(self):
        self._observers = []
    
    def register_observer(self, observer):
        if not observer in self._observers:
            self._observers.append(observer)
    
    def unregister_observer(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, message=None, arg=None):
        for obs in self._observers:
            obs.notify( message, arg )
        