# README #

EEGKiss project, by artists Hermen Maat and Karen Lancel.

### What is this repository for? ###

* Quick summary

EEGKiss project in python 2.7.

* Version

1.7

### How do I get set up? ###

* Installation

1) Checkout the repository
2) Install MuseDirect
3) Install SuperCollider

a) Make sure the SuperCollider is 64-bit on a 64-bit system. Make sure the latest version is installed. (3.8.8 was needed to make it work on the latest machine).

b) Add startup.scd to C:\Users\maat\AppData\Local\SuperCollider (which is variable Platform.userConfigDir in SuperCollider)

c) Make sure line 275 in startup.scd refers to an existing folder.
	e.g.: b.write("C:/Users/EEG Kiss/Documents/EEG-Kiss/Tools/eegrecs" ++ (~spaceCount/5).asInt.asString ++"EegSoundRec.wav", "wav", "int16", 0, 0, true);

4) Install Python 2.7, use pip to install the dependencies mentioned below
5) Pair the Muse Headsets to the PC.
6) Find the Muse Headsets using Muse Direct.
7) Set up Muse Direct as described below and in the example images.

* Configuration

In the repository there is an .sln file: this is a visual studio project solution file, usually used for c++ projects. Sometimes also used for python projects. 
I have been able to use this .sln file to view the files, and search through them using VS standard search tools. 
I have not been able to use visual studio to run the python code. I used command line for that.
To start the version that uses Muse, start applicationmain with parameters 'useMuse'. 
I split the EEG_KISS_Run.bat into two .bat files, one for Muse and one for Imec. EEG_KISS_Run_Muse.bat starts applicationmain.py with 'useMuse'.
* Dependencies

. python 2.7

Install using pip:

. Cython

. pyOSC

. numpy

. matplotlib

. py2exe-py2

. pyBluez

. scipy

. pyserial


* Adaptations

I made some minor changes to the OSC.py file to support 'd' (doubles) and OSC addresses that do not start with a '/'.
MuseDirect is used to connect to the muse headsets and provides an interface to deal with that.

. MuseDirect sends out OSC messages without a '/' at the beginning of the address (for example 'eegkiss/eeg'). However, OSC.py did not support receiving addresses without a '/' at the beginning. 
Thus two lines of code were commented in OSC.py in 'addMsgHandler'.

. MuseDirect sends out OSC messages with doubles. OSC.py did not support receiving doubles (only floats, ints, string.. etc.). Thus I added '_readDouble'. 

. The changed OSC.py can be found in Source/EEG-KISS-Project/osc

. A better way to do this would be to fork the existing pyOSC git and make these changes, then refer to this fork when installing pyOSC using pip. 

### Muse Direct ###

Send to UDP localhost:7001 for the first muse headset, and localhost:7002 for the second muse headset.
See an example of the Muse Direct settings in 'MuseDirectSettingsExample.png'

### Who do I talk to? ###

. maat@xs4all.nl

. Baltan laboratories

. dirkbroenink.nl

. EagleScience


(this readme was written by Dirk Broenink on 18-12-2017)