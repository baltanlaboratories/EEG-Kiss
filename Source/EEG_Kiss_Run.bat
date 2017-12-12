set PATH=%PATH%;C:\Python27EEG
set PYTHONPATH=%CD%\EEG-KISS-Project;C:\Python27EEG\lib\site-packages\mne-0.9.dev0-py2.7.egg;C:\Python27EEG\DLLs;C:\Python27EEG\lib;C:\Python27EEG\lib\lib-tk;C:\Python27EEG;C:\Python27EEG\lib\site-packages

rem Python interpreter must be installed directly under C:\ and should be named Python27EEG.
rem This batch file must be placed at the same heigth as the "EEG-KISS-Project" directory

cd .\EEG-KISS-Project\root\gui
python -m applicationmain
cd ..\..\..