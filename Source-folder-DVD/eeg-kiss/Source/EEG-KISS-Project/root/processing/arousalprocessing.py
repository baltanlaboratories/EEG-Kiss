'''
Created on Jul 17, 2015

@author: tim.hermans
'''
import logging

from root.core.syncdataconsumer import SyncDataConsumer
from root.core.constants import PatternStrings, VisualisationTypes

class ArousalProcessor(SyncDataConsumer):
    '''
    classdocs
    '''


    def __init__(self, blackboard, patterns, type=None):
        """You should present 4 patterns, channel 1 and 3 of alpha and beta waves"""
        
        self.type = type
        
        for pattern in patterns:
            if PatternStrings.CHANNEL + "1" in pattern:
                if PatternStrings.ALPHA in pattern:
                    self.a_1 = pattern
                elif PatternStrings.BETA in pattern:
                    self.b_1 = pattern
            elif PatternStrings.CHANNEL + "3" in pattern:
                if PatternStrings.ALPHA in pattern:
                    self.a_3 = pattern
                elif PatternStrings.BETA in pattern:
                    self.b_3 = pattern
        
        if hasattr(self, 'a_1') and hasattr(self, 'a_3') and hasattr(self, 'b_1') and hasattr(self, 'b_3')and (self.a_1 and self.a_3 and self.b_1 and self.b_3):
            SyncDataConsumer.__init__(self, blackboard, patterns)
        else:
            raise ValueError("Not all required patterns were provided")
    
        self.logger = logging.getLogger()        
    
    def _process_data(self, pattern, data, timestamps):
        
        #print data, timestamps
        headset = pattern[0][:6] 
        if len(timestamps) == 1:
            arousal = self.calculate(data[self.a_1][0], data[self.a_3][0], data[self.b_1][0], data[self.b_3][0])
            self.blackboard.put_data(headset + PatternStrings.AROUSAL, arousal, timestamps[0])
        else:
            for index in range(len(timestamps)):
                arousal = self.calculate(data[self.a_1][index], data[self.a_3][index], data[self.b_1][index], data[self.b_3][index])
                self.blackboard.put_data(headset + PatternStrings.AROUSAL, arousal, timestamps[index])
          
    def set_calculation_type(self, type):
        self.logger.log(logging.INFO, (__file__, ": Changed calculation type to: ", type))       
        self.type = type
          
    def calculate(self, a_1, a_3, b_1, b_3):
#         print self.type
        if self.type == VisualisationTypes.AROUSEL:
            return self.calculate_arousal(a_1, a_3, b_1, b_3)
        elif self.type == VisualisationTypes.VALENCE:
            return self.calculate_valence(a_1, a_3, b_1, b_3)
        else:
            return 0
        
    def calculate_arousal(self, a_1, a_3, b_1, b_3):
        if a_1 and a_3 and b_1 and b_3:
#             print "Arousal"
            return (b_1+b_3)/(a_1+a_3)
        else:
            raise ValueError("Not all required patterns were provided")
        
    def calculate_valence(self, a_1, a_3, b_1, b_3):
        if a_1 and a_3 and b_1 and b_3:
#             print "Valence"
            return (a_3/b_3)-(a_1/b_1)
        else:
            raise ValueError("Not all required patterns were provided")
        