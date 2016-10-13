set PATH=%PATH%;C:\Python27EEG
set PYTHONPATH=%CD%\EEG-KISS-Project;C:\Python27EEG\lib\site-packages\mne-0.9.dev0-py2.7.egg;C:\Python27EEG\DLLs;C:\Python27EEG\lib;C:\Python27EEG\lib\lib-tk;C:\Python27EEG;C:\Python27EEG\lib\site-packages

@echo off
rem Python interpreter must be installed directly under C:\ and should be named Python27EEG.
rem This batch file must be placed at the same heigth as the "EEG-KISS-Project" directory

cd .\EEG-KISS-Project\headset_simulator
rem python -m serial_simulator -ch1 30 250 -ch2 6 500 -ch3 9 1000 -ch4 12 2000 -r -p COM14
python -m serial_simulator -p COM14
