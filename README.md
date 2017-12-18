# README #

EEGKiss project, by artists Hermen Maat and Karen Lancel.

### What is this repository for? ###

* Quick summary
EEGKiss project in python 2.7.
* Version 
1.7

### How do I get set up? ###

* Configuration
In the repository there is an .sln file: this is a visual studio project solution file, usually used for c++ projects. Sometimes also used for python projects. 
I have been able to use this .sln file to view the files, and search through them using VS standard search tools. 
I have not been able to use visual studio to run the python code. I used command line for that.
* Dependencies
. python 2.7
pip freeze:
- pyOSC
* Adaptations
I made some minor changes to the OSC.py file to support 'd' (doubles) and OSC addresses that do not start with a '/'.
MuseDirect is used to connect to the muse headsets and provides an interface to deal with that.
. MuseDirect sends out OSC messages without a '/' at the beginning of the address (for example 'eegkiss/eeg'). However, OSC.py did not support receiving addresses without a '/' at the beginning. 
Thus two lines of code were commented in OSC.py in 'addMsgHandler'.
. MuseDirect sends out OSC messages with doubles. OSC.py did not support receiving doubles (only floats, ints, string.. etc.). Thus I added '_readDouble'. 


### Muse Direct ###

Send to UDP localhost:7001 for the first muse headset, and localhost:7002 for the second muse headset.


### Who do I talk to? ###

. maat@xs4all.nl
. Baltan laboratories
. dirkbroenink.nl
. EagleScience

(this readme was written by Dirk Broenink on 18-12-2017)