'''
Created on Jul 1, 2015

@author: tim.hermans
'''
import OSC
from root.core.blackboard               import Blackboard 
from root.core.dataconsumer             import DataConsumer
from root.core.observerpattern          import Subject

class OscWriter ( DataConsumer, Subject ):
    
    def __init__(self, blackboard, patterns):
        """
        @param blackboard:
            blackboard instance which contains the data that must be plotted
        @param patterns
            the patterns corresponding to the data buffers that must be plotted
        """
        
        if not isinstance(blackboard, Blackboard):
            raise ValueError("blackboard should be Blackboard instance")
        
        if not isinstance(patterns, list):
            if isinstance(patterns, str):
                patterns = [patterns]
            else:
                raise ValueError("patterns should be string or list of strings")
            
        Subject.__init__( self )
        DataConsumer.__init__(self, blackboard, patterns)
            
        self.blackboard     = blackboard
        self._patterns      = patterns

        self.client = OSC.OSCClient()
        self.client_port7112 = OSC.OSCClient()
        self.client.connect(('127.0.0.1', 7110))          # connection for openFramework application (radar-visualisation)
        # self.client.connect(('172.16.10.83', 7110))      # Test connection with PC-system of Pim M.
        self.client_port7112.connect(('127.0.0.1', 7112)) # connection for SuperCollider application (audio)
        
    def _process_data(self, pattern, data, timestamps):
        for sample in data:
            oscmsg = OSC.OSCMessage()
            oscmsg.setAddress(pattern)
#             if '/markers' in pattern:
#                 print pattern, sample, timestamps
            oscmsg.append(sample/4096.)
            self.client.send(oscmsg)
            self.client_port7112.send(oscmsg)
