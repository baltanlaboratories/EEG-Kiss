'''
Created on Jun 17, 2015

@author: tim.hermans
'''
from Tkinter import IntVar, StringVar
from root.core.constants import ChannelTypes, FrequencyBands

class TimeSettings:
    '''
    Used to pass common settings
    '''

    def __init__(self):
        self.channel = {}
        self.channel[ChannelTypes.LEFT] = IntVar()
        self.channel[ChannelTypes.MID] = IntVar()
        self.channel[ChannelTypes.RIGHT] = IntVar()
        self.channel[ChannelTypes.BACK] = IntVar()
        self.showLabels = IntVar()
        
        self.channel[ChannelTypes.LEFT].set(1)
        self.channel[ChannelTypes.MID].set(1)
        self.channel[ChannelTypes.RIGHT].set(1)
        self.channel[ChannelTypes.BACK].set(1)
        self.showLabels.set(1)
        
    def getCopy(self):
        copy = TimeSettings();
        copy.channel[ChannelTypes.LEFT].set(self.channel[ChannelTypes.LEFT].get())
        copy.channel[ChannelTypes.MID].set(self.channel[ChannelTypes.MID].get())
        copy.channel[ChannelTypes.RIGHT].set(self.channel[ChannelTypes.RIGHT].get())
        copy.channel[ChannelTypes.BACK].set(self.channel[ChannelTypes.BACK].get())
        copy.showLabels.set(self.showLabels.get())
        return copy
    
    def update(self, other):
        self.channel[ChannelTypes.LEFT].set(other.channel[ChannelTypes.LEFT].get())
        self.channel[ChannelTypes.MID].set(other.channel[ChannelTypes.MID].get())
        self.channel[ChannelTypes.RIGHT].set(other.channel[ChannelTypes.RIGHT].get())
        self.channel[ChannelTypes.BACK].set(other.channel[ChannelTypes.BACK].get())
        self.showLabels.set(other.showLabels.get())
        
    def get_showLabels(self):
        if self.showLabels.get()==1:
            return True
        else:
            return False

class FrequencyBandSettings ():
    '''
    Used to pass common settings
    '''

    def __init__(self):
        self.channel = {}
        self.channel[ChannelTypes.LEFT] = IntVar()
        self.channel[ChannelTypes.MID] = IntVar()
        self.channel[ChannelTypes.RIGHT] = IntVar()
        self.channel[ChannelTypes.BACK] = IntVar()
        self.showLabels = IntVar()
        self.frequencyBand = StringVar()
        
        self.channel[ChannelTypes.LEFT].set(1)
        self.channel[ChannelTypes.MID].set(1)
        self.channel[ChannelTypes.RIGHT].set(1)
        self.channel[ChannelTypes.BACK].set(1)
        self.showLabels.set(1)
        self.frequencyBand.set(FrequencyBands.ALPHA)
        
    def getCopy(self):
        copy = FrequencyBandSettings();
        copy.channel[ChannelTypes.LEFT].set(self.channel[ChannelTypes.LEFT].get())
        copy.channel[ChannelTypes.MID].set(self.channel[ChannelTypes.MID].get())
        copy.channel[ChannelTypes.RIGHT].set(self.channel[ChannelTypes.RIGHT].get())
        copy.channel[ChannelTypes.BACK].set(self.channel[ChannelTypes.BACK].get())
        copy.showLabels.set(self.showLabels.get())
        copy.frequencyBand = self.frequencyBand
        return copy
    
    def update(self, other):
        self.channel[ChannelTypes.LEFT].set(other.channel[ChannelTypes.LEFT].get())
        self.channel[ChannelTypes.MID].set(other.channel[ChannelTypes.MID].get())
        self.channel[ChannelTypes.RIGHT].set(other.channel[ChannelTypes.RIGHT].get())
        self.channel[ChannelTypes.BACK].set(other.channel[ChannelTypes.BACK].get())
        self.showLabels.set(other.showLabels.get())
        self.frequencyBand = other.frequencyBand
        
    def get_showLabels(self):
        if self.showLabels.get()==1:
            return True
        else:
            return False


class SpectrumSettings:
    '''
    Used to pass common settings
    '''

    def __init__(self):
        self.channel = {}
        self.channel[ChannelTypes.LEFT] = IntVar()
        self.channel[ChannelTypes.MID] = IntVar()
        self.channel[ChannelTypes.RIGHT] = IntVar()
        self.channel[ChannelTypes.BACK] = IntVar()
        self.showLabels = IntVar()
        
        self.channel[ChannelTypes.LEFT].set(1)
        self.channel[ChannelTypes.MID].set(1)
        self.channel[ChannelTypes.RIGHT].set(1)
        self.channel[ChannelTypes.BACK].set(1)
        self.showLabels.set(1)
        
    def getCopy(self):
        copy = SpectrumSettings();
        copy.channel[ChannelTypes.LEFT].set(self.channel[ChannelTypes.LEFT].get())
        copy.channel[ChannelTypes.MID].set(self.channel[ChannelTypes.MID].get())
        copy.channel[ChannelTypes.RIGHT].set(self.channel[ChannelTypes.RIGHT].get())
        copy.channel[ChannelTypes.BACK].set(self.channel[ChannelTypes.BACK].get())
        copy.showLabels.set(self.showLabels.get())
        return copy
    
    def update(self, other):
        self.channel[ChannelTypes.LEFT].set(other.channel[ChannelTypes.LEFT].get())
        self.channel[ChannelTypes.MID].set(other.channel[ChannelTypes.MID].get())
        self.channel[ChannelTypes.RIGHT].set(other.channel[ChannelTypes.RIGHT].get())
        self.channel[ChannelTypes.BACK].set(other.channel[ChannelTypes.BACK].get())
        self.showLabels.set(other.showLabels.get())
        
    def get_showLabels(self):
        if self.showLabels.get()==1:
            return True
        else:
            return False