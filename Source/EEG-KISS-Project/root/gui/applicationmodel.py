'''
Created on 23 apr. 2015

@author: Bas.Kooiker
'''

import os
import threading

from root.core.blackboard               import Blackboard
from root.core.settings                 import TimeSettings, FrequencyBandSettings, SpectrumSettings
from root.input.imecinput               import ImecInput
from root.input.museinput               import MuseInput
from root.input.datasimulator           import DataSimulator
from root.input.timedsimulator          import TimedSimulator
from root.output.filerecorder           import FileRecorder
from root.processing.fftanalyzer        import FFTAnalyzer
from root.core.observerpattern          import Subject
from root.processing.firfilter          import FIRFilter
from root.core.coretime                 import CoreTime
from root.output.imecwriter             import IMECWriter
from root.core.constants                import States, PatternStrings, SignalNames, FilterSettings, ChannelTypes, VisualisationTypes
from time                               import sleep
from root.processing.arousalprocessing import ArousalProcessor
from _functools import partial


class ApplicationModel( Subject ):
    """
    This ApplicationModel is part of the MVC design pattern in conjunction with the ApplicationView and Application Controller.
    This model also serves as a factory, as it initializes all the components in the right way with the correct configuration.
    The components are all publicly available to the outside, though, they should be approached only through the applications controller.
    """ 
    
    def __init__(self, useMuse):
        Subject.__init__( self )
        self.nr_of_headsets = 5
        self.channels       =[1,2,3,4]
        
        self.blackboard     = Blackboard()
        self.simulators     = []
        self.headsets       = []
        self.processors     = []
        self.filerecorders  = []
        self.oscwriters     = []
        
        self._connected_headsets = 0
        self._useMuse = useMuse

        self.timeSettings = TimeSettings()
        self.frequencySpectrumSettings =SpectrumSettings()
        self.frequencyBandSettings = FrequencyBandSettings()
        
        # Initialize simulators
        for _ in range( self.nr_of_headsets ):
            self.simulators.append( TimedSimulator( self.blackboard ) ) 
        
        # Initialize headsets
        i = 0
        for headset in range( self.nr_of_headsets ):
            if self._useMuse:
                self.headsets.append( MuseInput(i, self.blackboard, PatternStrings.SIGNAL_EEG + '%d' % (headset) ) )
            else:
                self.headsets.append( ImecInput( self.blackboard, PatternStrings.SIGNAL_EEG + '%d' % (headset) ) )
            i += 1
        
        # Initialize preprocessing filters
        for i, channel in enumerate(self.channels):
            """
            for headset in range( self.nr_of_headsets ):
                pat = PatternStrings.SIGNAL_EEG + '%d' % (headset) + PatternStrings.CHANNEL + '%d' % (channel)
                
                # Add notch filtering
                notch = FIRFilter( self.blackboard, pat, FilterSettings.NOTCH_NUMTAPS, FilterSettings.NOTCH_FS, FilterSettings.NOTCH_FREQ, 'notch' )
                notch.start(name = 'fir_notch' + pat)
                self.processors.append( notch )
                
                pat += PatternStrings.FILTERNOTCH
                
                # Add low-pass filtering
                lpf = FIRFilter( self.blackboard, pat, FilterSettings.LPF_NUMTAPS, FilterSettings.LPF_FS, FilterSettings.LPF_FREQ, 'lpf' )
                lpf.start(name = 'fir_lpf' + pat)
                self.processors.append( lpf )
            """
                
        # Patterns that will be recorded
        patterns = []
        for headset in range(self.nr_of_headsets):
            patterns.append( [(PatternStrings.SIGNAL_EEG + '%d' % (headset) + PatternStrings.CHANNEL + '%d' % (i))
                               for i in self.channels])
            
        names = [SignalNames.RAWSIGNAL for _ in self.channels ]
        
        # Initialize recorders
        for i, pat in enumerate(patterns):
            rec = FileRecorder( self.blackboard, pat, self.channels, names, writer=IMECWriter() )
            rec.start( interval=10, name = 'recorder-%d' % i )
            self.filerecorders.append( rec )
        
        # Perform FFT only on raw signals
        patterns = []
        for headset in range(self.nr_of_headsets):
            patterns.append( [(PatternStrings.SIGNAL_EEG + '%d' % (headset) + PatternStrings.CHANNEL + '%d' % (i)) for i in self.channels] )
        
        # Initialize FFT analyzer
        freqspec = FFTAnalyzer(self.blackboard, sum(patterns, [])) # NOTE: Could be made faster by using for's i.s.o. sum, but for init-code not really relevant
        #freqspec.start() DO NOT START FFT AT INIT
        self.processors.append( freqspec )
        
        # Initialize Arousal processors
        for headset in range(self.nr_of_headsets):
            patterns = []
            for channel in [1,3]:
                for freq in [PatternStrings.ALPHA, PatternStrings.BETA]:
                    patterns.append(PatternStrings.SIGNAL_EEG + '%d' % (headset) + PatternStrings.CHANNEL + '%d' % (channel) + freq)
            
            # Initialize Arousal processor
            arousal = ArousalProcessor(self.blackboard, patterns)
            #arousal.start() DO NOT START ArousalProcessor AT INIT
            self.processors.append( arousal )

        
    ### Getters/Setters ###
    
    # ---------- Simulators ----------
    def get_simulation_state(self):
        """
        Returns simulation state {IDLE, PLAYING, PAUSED}
        """
        state  = DataSimulator.IDLE
        for sim in self.simulators:
            if sim:
                if sim._state == DataSimulator.PLAYING:
                    return sim._state
                elif sim._state == DataSimulator.PAUSED:
                    state = DataSimulator.PAUSED
        return state
    
    def get_simulation_time(self):
        """
        Returns the playback time of the first active data simulator. Or 0.
        """
        for sim in self.simulators:
            if sim.get_simulation_state() == DataSimulator.PLAYING:
                return sim.get_current_time()
        return 0
    
    def set_simulation_time(self, time):
        """
        Sets the playback time of all active data simulators
        """
        for sim in self.simulators:
            sim.set_time( time )
            
    def get_simulation_length(self):
        """
        Resturns the length of the shortest loaded data file
        """
        for sim in self.simulators:
            t = sim.get_total_time()
            i = [ sim.get_total_time() for sim in self.simulators if sim.get_total_time() > 0 ]

        return min( [ sim.get_total_time() for sim in self.simulators if sim.get_total_time() > 0 ] )
              
    def is_receiving_data(self):
        """
        Boolean whether at least one headset is streaming data or one channel is simulating data
        """
        return self.get_simulation_state() != DataSimulator.IDLE or self.is_headset_streaming()
             
    def is_recording(self):
        """
        Boolean whether at least one file recorder is recording data 
        """
        for rec in self.filerecorders:
            if rec:
                if rec.is_recording():
                    return True
        return False
    
    # ---------- Headsets ----------
    def is_headset_streaming(self): 
        """
        Boolean whether at least one headset is streaming data
        """
        for hs in self.headsets:
            if hs.is_streaming():
                return True
        return False
    
    def is_headset_connected(self):
        """
        Boolean whether at least one headset is connected
        """
        count = 0
        for hs in self.headsets:
            if hs.is_connected():
                count += 1

        print ('count', count)
        print ('connected headsets', self._connected_headsets)

        if count > 0 and count >= self._connected_headsets:
            return True

        return False
    
    def is_headset_serial_busy(self):
        for hs in self.headsets:
            if hs.get_serial_state() == States.BUSY:
                return True
        return False
    
    def get_headset_time(self):
        """
        Returns the latest headset time. Or 0 if none of the headsets is streaming.
        """
        time = 0;
        for hs in self.headsets:
            if hs.is_connected():
                hs_time = hs.get_time()
                if hs_time > time:
                    time = hs_time
        return time
    
    def get_headset_duration(self):
        """
        Returns the headset duration-time since last start. Or 0 if none of the headsets is streaming.
        """
        time = 0;
        for hs in self.headsets:
            if hs.is_connected():
                hs_time = hs.get_duration()
                if hs_time > time:
                    time = hs_time
        return time
    
    def get_recording_duration(self):
        """
        Returns the recording duration-time since start recording. Or 0 if none of the headsets is being recorded.
        """
        time = 0;
        for rec in self.filerecorders:
            if rec:
                if rec.is_recording():
                    rec_time = rec.get_duration()
                    if rec_time > time:
                        time = rec_time

        return time
    
    ### Methods ### All these methods should call notify_observers() in order to update the controller and view components
    def start_headsets(self):
        """
        Starts all initialized headsets
        """
        for i, hs in enumerate(self.headsets):
            if hs:
                print ('headset-%d start'% i)
                if self._useMuse:
                    hs.start(i, 'headset-%d' % i)
                else:
                    hs.start(i)
        self.notify_observers()
                 
    def stop_headsets( self ):
        """
        Stops all active headsets
        """
        for hs in self.headsets:
            if hs:
                hs.stop()
        self.notify_observers('stop_streaming')
        
    def send_get_battery_commands(self):
        """
        Send command to all headsets requesting their battery levels 
        """
        for hs in self.headsets:
            if hs and hs.is_connected():
#                 if not hs.send_get_command('Battery'):
                hs.send_battery_command()
        
    def start_simulation( self ):
        """
        Starts all active simulators
        """
        CoreTime().reset()
        for i, sim in enumerate(self.simulators):
            if sim:
                try:
                    sim.start(name = 'simulator-%d' % i)
                except Exception as e:
                    print 'Exception start_simulation:', e
        self.notify_observers()
             
    def pause_simulation( self ):
        """
        Stops all active simulators
        """
        for sim in self.simulators:
            if sim:
                sim.pause()
        self.notify_observers()
        
    def stop_simulation( self ):
        """
        Stops all active simulators
        """
        for sim in self.simulators:
            if sim:
                try:
                    sim.stop()
                except Exception as e:
                    print 'Exception stop_simulation:', e
        
        self.notify_observers()
    
    def set_headset_connection(self, index, socket = None):
        if index >= 0 and index < len(self.headsets) and socket != None:
            self.headsets[index].set_connection(socket)
            self._connected_headsets += 1
            return True

        return False

    def add_muse_headset_connection(self):
        self._connected_headsets = 2
    
    def get_connected_headsets(self):
        return self._connected_headsets

    def disconnect_headsets(self):
        for hs in self.headsets:
            hs.disconnect()
            if self._connected_headsets > 0:
                self._connected_headsets -= 1

    def set_foldername(self):
        self.foldername = 'data'
        for index in range(self.nr_of_headsets):
            self.foldername += '_' + self.filerecorders[index].get_filename()
        print self.foldername
        file = open(os.path.dirname(__file__) + '\\..\\..\\..\\subfolder.txt', 'w')
        file.write(self.foldername)
        file.close()
        
    
    def set_filename(self, index, filename ):
        """ 
        Set the name of the recod-file for one of the headsets
        """
        self.filerecorders[index].set_filename( filename )
        self.notify_observers()
        
    def start_recording(self, time):
        """
        Start recording with all initialized recorders
        """
        for rec in self.filerecorders:
            rec.start_recording(time)
            
        self.notify_observers()

    def stop_recording(self):
        """
        Stop recording with all active recorders
        """
        for rec in self.filerecorders:
            rec.stop_recording()
        self.notify_observers()
    
    def get_data_sources(self):
        """
        Finds all Observer pattern subjects in the model 
        """
        components = self.simulators + self.processors + self.filerecorders
        return  [s for s in components if hasattr(s,"process_step") ]
    
    def get_active_channels(self, activeVisualisation):
        
        if (activeVisualisation == VisualisationTypes.TIME):
            settings = self.timeSettings
        elif (activeVisualisation == VisualisationTypes.FREQUENCY):
            settings = self.frequencySpectrumSettings
        elif (activeVisualisation == VisualisationTypes.FREQUENCY_BAND):
            settings = self.frequencyBandSettings
        else:
            return 'You have to edit this method if you add a new visualisationType'
        
        values=[]
        #KEEP THIS ORDER! This is the order of the input channels
        if settings.channel[ChannelTypes.RIGHT].get()==1:
            values.append(ChannelTypes.values[ChannelTypes.RIGHT])
            
        if settings.channel[ChannelTypes.MID].get()==1:
            values.append(ChannelTypes.values[ChannelTypes.MID])
        
        if settings.channel[ChannelTypes.LEFT].get()==1:
            values.append(ChannelTypes.values[ChannelTypes.LEFT])
        
        if settings.channel[ChannelTypes.BACK].get()==1:
            values.append(ChannelTypes.values[ChannelTypes.BACK])
        
        return values

    ##### Subject components #####    
    def subjects(self):
        """
        Finds all Observer pattern subjects in the model 
        """
        subjects = self.simulators + self.headsets + self.processors + self.filerecorders
        return [s for s in subjects if hasattr(s,"notify_observers") ]
        
    def register_observer(self, observer):
        """
        Overrides from Subject
        """
        Subject.register_observer(self, observer)
        for subject in self.subjects():
            subject.register_observer( observer )
    
    def unregister_observer(self, observer):
        """
        Overrides from Subject
        """
        Subject.unregister_observer(self, observer)
        for subject in self.subjects():
            subject.unregister_observer( observer )
