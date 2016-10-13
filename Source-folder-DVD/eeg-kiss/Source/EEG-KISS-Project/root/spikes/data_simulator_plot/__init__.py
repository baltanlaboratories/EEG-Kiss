'''
Read paired EEG data from two people and play it back.

The simulated EEG data is send over OSC over the localhost port 8000.

The data is caught by the second process for further processing.

This further processing is 

pyOSC works on Python 2.7

MultiProcessing is used instead of Threads because MatPlotLib does not work
on a sub-thread. It does work on a sub-process.

Two instances of oscdatasimulator are used to playback two EEG files. B

Download pyOSC from https://trac.v2.nl/wiki/pyOSC
'''
from dummyplotwidget import DummyPlotWidget