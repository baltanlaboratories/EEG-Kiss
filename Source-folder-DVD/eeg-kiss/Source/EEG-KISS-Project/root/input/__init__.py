'''
The input package contains all input modules for the EEG-Kiss framework. 
These modules contain both offline as online data sources.
Offline data sources include filereaders such that data can be loaded from the hard disk.
Online data sources are streams of data, for instance from an EEG headset or online sources.
'''
import hdfreader
import datasimulator
import imecinput
