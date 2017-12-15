'''
Created on 23 apr. 2015

@author: Bas.Kooiker
'''
import os
import tkFileDialog
import logging

from functools                          import partial

from root.core.constants                import Markers, PatternStrings, VisualisationTypes, ChannelTypes, FrequencyBands, \
    Testing
from root.core.settings                 import TimeSettings, FrequencyBandSettings,\
    SpectrumSettings
from root.input.datasimulator           import DataSimulator
from root.input.hdfreader               import HDFReader
from root.core.observerpattern          import Observer
from root.input.timedsimulator          import TimedSimulator
from root.output.timedsignalplot        import TimedSignalPlot
from root.processing.firfilter          import FIRFilter
from root.processing.fftanalyzer        import FFTAnalyzer
from root.output.oscwriter              import OscWriter
from root.core.processingthread         import ProcessingThread
from root.output.spectrumsignalplot     import SpectrumSignalPlot
from root.processing.arousalprocessing import ArousalProcessor
from time import sleep
from root.connectivity.bluetooth_connection import Bluetooth
from root.connectivity.serial_connection import SerialSocket
from Tkinter import IntVar


class ScrollController:
    """
    Little specific helper class for handling user input.
    Divides the scrollbar listener in a mouse down and mouse up listener
    A state is stored on mouse down which is used on mouse up 
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.prestate = DataSimulator.IDLE
    
    def press_listener(self, event):
        """
        The current Simulation state is stored and if necessary, simulation is paused
        """
        self.prestate = self.parent.model.get_simulation_state()
        if self.prestate == DataSimulator.PLAYING:
            self.parent.model.pause_simulation()
    
    def release_listener(self, event):
        """
        If simulation was playing, it is restarted.
        """
        self.parent.set_playback_time( event.widget.get() )
        if self.prestate == DataSimulator.PLAYING:
            self.parent.model.start_simulation()
        self.parent.notify()


class UpdateTimeController(ProcessingThread):
    """
    Helper class for updating the second counters shown when streaming/recording headset-data.
    A separate thread is started which sets a global flag each 0.5 s.
    This flag is polled in main-thread, because application crashes when the ttk-labels are updated from this thread.
    """
    def __init__(self, parent):
        ProcessingThread.__init__( self )
        self._parent = parent
    
    def process_step(self):
        self._parent._checkTime = True
    
    def start(self, interval=500, name='no_name'):
        ProcessingThread.start(self, interval=interval, name=name)


class ApplicationController( Observer ):
    ''' 
    Class for the EEG application UI 
    Two data files of headset streams can be opened. Pre-specified parts of these data streams are plotted in the GUI
    '''

    def __init__(self, model, view, useMuse ):
        """
        This Controller initializes the Model and the View.
        Then, in infinite loop is started that will update the application components.
            
        @param model:
            The application model
        @param view:
            The application view
        """
        self.logger = logging.getLogger()
        
        self._plots = []
        self._running           = True
        self._restartPlayback   = False
        self._checkTime         = False
        self._bluetooth         = None
        self._kissing           = False
        self._useMuse           = useMuse
        
        self.play_loopmode = IntVar()

        # Initialize model and controller
        self.model  = model
        self.view   = view 
    
        self.initialize_callbacks()
        self.model.register_observer( self )
        self.view.register_observer( self )
        self.initialize_time_plots()
        
        for plot in self._plots:
            plot.register_observer( self )
        
        self.time_controller = UpdateTimeController(self)
        
        #Register for close window event
        self.view.root.protocol("WM_DELETE_WINDOW", self.shutdown_ttk_repeat)
        
        
    def shutdown_ttk_repeat(self):
        self.logger.log(logging.INFO, (os.path.basename(__file__) + ': EXIT NOW'))

        self.view.root.eval('::ttk::CancelRepeat')
        self.view.root.destroy()
        self.view.root.quit()
        
        # Stop thread thats updating the view, view is destroyed!
        self._running = False
        
        
    def update_gui_forever(self):
        """
        Start view and infinite controller update loop
        """
        self.view.start()
        
        while self._running:
            for plot in self._plots:
                plot.show()
                
            try:
                self.view.canvas.draw()
            except:
                self.logger.log(logging.ERROR, (__file__, ": applicationcontroller.py: An exception was thrown when drawing the canvas"))
                
            try:
                self.view.root.update()
            except:
                self.logger.log(logging.ERROR, (__file__, ": applicationcontroller.py: An exception was thrown when updating the view"))
            
            if self._restartPlayback:
                self.toggle_playback()
                self._restartPlayback = False
            
            if self._checkTime:
                self._checkTime = False
                if self.model.is_headset_streaming():
                    stream_time = self.model.get_headset_duration()
                    self.view.stream_counter_value.set('%d' % stream_time)
                    if self.model.is_recording():
                        rec_time = self.model.get_recording_duration()
                        self.view.rec_counter_value.set('%d' % rec_time)
    
    
    def initialize_callbacks(self):
        """
        Defines the coupling of GUI elements to controller callbacks
        """
        self.view.rb_sim.config( command=self.select_mode_simulating)
        self.view.rb_stream.config( command=self.select_mode_streaming )
        self.view.cb_display.bind("<<ComboboxSelected>>", partial(self.visualisationTypeChanged))
        self.view.b_display_settings.config( command=partial(self.show_display_settings))
        
        for i in range( self.model.nr_of_headsets ):
            self.view.browse_buttons[i].config( command=partial( self.file_open, i ) )
            self.view.clear_buttons[i].config( command=partial( self.clear_filename, i ) )
        
        self.view.btn_connect.config(command = self.toggle_headset_connection)
        
        self.view.b_toggle_simulation.config( command=self.toggle_playback )
        self.view.b_stop_simulation.config( command=self.stop_playback )
        
        self.view.cb_loopmode.config(variable = self.play_loopmode, command = self.toggle_play_loopmode)
        
        self.view.b_toggle_streaming.config( command=self.toggle_streaming )
        self.view.b_toggle_recording.config( command=self.toggle_recording )
        
        self.view.zoom_sliders[0].config( command=self.set_xrange )
        self.view.zoom_sliders[1].config( command=self.set_yrange )
        
        sc = ScrollController( self )
        self.view.plot_scrollbar.bind("<ButtonPress-1>", sc.press_listener )
        self.view.plot_scrollbar.bind("<ButtonRelease-1>", sc.release_listener )
        
        self.view.b_start_kiss.config( command=self.start_kiss_marker )
        self.view.b_stop_kiss.config( command=self.stop_kiss_marker )
        self.view.b_poi.config( command=self.poi_marker )
        
        # Call custom method on close 
        self.view.root.protocol( 'WM_DELETE_WINDOW', self.ask_quit )
        
    def set_playback_time(self, time ):
        """
        Sets a desired time for the DataSimulators in the model and resets the plot widgets
        """
        self.model.set_simulation_time( time )
        for p in self._plots:
            p.reset()
        
    def start_kiss_marker(self):
        """
        Adds the start marker to the blackboard
        """
        time = self.model.get_headset_time()
        self.logger.log(logging.INFO, (__file__, ": applicationcontroller.py: Start kiss: ", time))
        self.model.blackboard.put_data( PatternStrings.MARKERS, Markers.KISS_START, time )
        self._kissing = True
    
    def stop_kiss_marker(self):
        """
        Adds the stop marker to the blackboard
        """
        time = self.model.get_headset_time()
        self.logger.log(logging.INFO, (__file__, ": applicationcontroller.py: Stop kiss: ", time))
        self.model.blackboard.put_data( PatternStrings.MARKERS, Markers.KISS_STOP, time )
        self._kissing = False
    
    def poi_marker(self):
        """
        Adds the point of interest marker to the blackboard
        """
        time = self.model.get_headset_time()
        self.logger.log(logging.INFO, (__file__, ": applicationcontroller.py: Point of interest: ", time))
        self.model.blackboard.put_data( PatternStrings.MARKERS, Markers.POI, time )

    def set_xrange(self, value):
        """
        Sets the crop factor of the plot's x range
        """
        value = float(value)
        for plot in self._plots:
            #print "xLim:", value
            plot.plotConfig( xLim=value )
      
    def set_yrange(self, value):
        """
        Sets the range of the plot's y range
        """
        new_range = int(float(value))
        
        for plot in self._plots:
            plot.plotConfig( yrange = new_range )

            if (self.view.cb_display_value.get() in [VisualisationTypes.TIME, VisualisationTypes.FREQUENCY, VisualisationTypes.FREQUENCY_BAND, VisualisationTypes.AROUSEL]):
                #print "yoffset: ", plot.get_offset_last_samples(), "yrange: ", range
                plot.plotConfig(yoffset = plot.get_offset_last_samples())

    
    def set_yoffset(self, offset):
        for plot in self._plots:
            plot.plotConfig( yoffset = offset )
    
    def clean_active_plots(self):
        for plot in self._plots:
            plot.stop()
            plot.unregister_observer(self)
        self._plots=[]
    
    def initialize_time_plots(self):
        """
        Creates the plot widgets based on the axes in the view
        """
        self.clean_active_plots()
        axes = self.view.get_axes()
        self._plots = []
        
#         pats = []
#         pats.append(PatternStrings.MARKERS)
#         
#         oscWriter = OscWriter(self.model.blackboard, pats)
#         
#         try:
#             oscWriter.start(name = 'oscWriter-markers')
#             self.model.oscwriters.append(oscWriter)
#         except Exception as e:
#             self.logger.log(logging.ERROR, (__file__, ": applicationcontroller.py: An error occured in while writing time plot kiss markers to the oscwriter: ", e))
        
        # create plotters
        for i, channel in enumerate(self.model.get_active_channels(VisualisationTypes.TIME)):
            pats = []
            for headset in range(self.model.nr_of_headsets):
                pats.append(PatternStrings.SIGNAL_EEG + '%d' % (headset) + PatternStrings.CHANNEL + '%d' % (channel) + PatternStrings.FILTERNOTCH + PatternStrings.FILTERLPF)
            pw = TimedSignalPlot(self.model.blackboard, pats, ax = axes[i], marker_pattern = PatternStrings.MARKERS, name=ChannelTypes.names[channel], showLabel=self.model.timeSettings.get_showLabels())
#             pw = SignalPlot(self.model.blackboard, pats, ax = axes[i], name=ChannelTypes.names[channel], showLabel=self.model.timeSettings.get_showLabels())
            self._plots.append(pw)

            oscWriter = OscWriter(self.model.blackboard, pats)
            try:
                oscWriter.start(name = 'oscWriter-%d' % channel)
                self.model.oscwriters.append(oscWriter)
            except Exception as e:
                self.logger.log(logging.ERROR, (__file__, ": applicationcontroller.py: An error occured in while writing time plot channel data to the oscwriter: ", e))
                            
        # Setting sliders must be done outside the for-loop
        self.view.set_xslider(min_zoom = 0, max_zoom = 0.975, zoom_set = 0.2)
        self.view.set_yslider(min_zoom = 1000, max_zoom = 12000, zoom_set = 4000)
        
        # It appears that setting of the sliders also activates their callback, which sets yoffet to 0.
        # So set plot-configs to initial values after slider-initialization.
        # And start the plot-threads.
        for i, p in enumerate(self._plots):
            p.plotConfig(length = 8000, yoffset = 2000, yrange = 4000)
            p.start(name = 'signal_plot-%d' % i)
    
    def initialize_frequency_band_plots(self):
        """
        Creates the plot widgets based on the axes in the view
        """
        self.clean_active_plots()
        axes = self.view.get_axes()
        self._plots = []
        # create plotters
        for i, channel in enumerate(self.model.get_active_channels(VisualisationTypes.FREQUENCY_BAND)):
            pats = []
            for headset in range(self.model.nr_of_headsets):
                pats.append(PatternStrings.SIGNAL_EEG + '%d' % (headset) + PatternStrings.CHANNEL + '%d' % (channel) + FrequencyBands.patterns[self.model.frequencyBandSettings.frequencyBand.get()])

            pw = TimedSignalPlot(self.model.blackboard, pats, ax = axes[i], marker_pattern = PatternStrings.MARKERS, name=ChannelTypes.names[channel], showLabel=self.model.frequencyBandSettings.get_showLabels())
            pw.plotConfig(length = 8000, yoffset = 200, yrange = 400)
            pw.start(name = 'freqband_plot-%d' % channel)
            self._plots.append(pw)
            
            oscWriter = OscWriter(self.model.blackboard, pats)
            try:
                oscWriter.start()
                self.model.oscwriters.append(oscWriter)
            except Exception as e:
                self.logger.log(logging.ERROR, (__file__, ": applicationcontroller.py: An error occured in while writing frequency band channel data to the oscwriter: ", e))

        # Setting sliders must be done outside the for-loop
        self.view.set_xslider( min_zoom = 0, max_zoom = 0.975, zoom_set = 0.2)
        self.view.set_yslider( min_zoom = 10, max_zoom = 800, zoom_set = 400)
    
    def initialize_frequency_spectrum_plots(self):
        """
        Creates the plot widgets based on the axes in the view
        """
        self.clean_active_plots()
        axes = self.view.get_axes()
        self._plots = []
        # create plotters
        for i, channel in enumerate(self.model.get_active_channels(VisualisationTypes.FREQUENCY)):
            pats = []
            for headset in range(self.model.nr_of_headsets):
                pats.append(PatternStrings.SIGNAL_EEG + '%d' % (headset) + PatternStrings.CHANNEL + '%d' % (channel) + PatternStrings.FILTERNOTCH + PatternStrings.FILTERLPF + PatternStrings.FFT)

            pw = SpectrumSignalPlot(self.model.blackboard, pats, ax = axes[i], name=ChannelTypes.names[channel], showLabel=self.model.frequencySpectrumSettings.get_showLabels())
            pw.start(name = 'freqspec_plot-%d' % channel)
            self._plots.append(pw)
            
        # Setting sliders must be done outside the for-loop
        self.view.set_xslider( min_zoom = 10, max_zoom = 64, zoom_set = 64)
        self.view.set_yslider( min_zoom = 250, max_zoom = 5000, zoom_set = 2000)
            
    def initialize_arousal_plot(self):
        """
        Creates the plot widgets based on the axes in the view
        """
        self.clean_active_plots()
        axes = self.view.get_axes()
        self._plots = []
        # create plotters
        pats = []
        for headset in range(self.model.nr_of_headsets):
            pats.append(PatternStrings.SIGNAL_EEG + '%d' % (headset) + PatternStrings.AROUSAL)

        pw =  TimedSignalPlot(self.model.blackboard, pats, ax = axes[0], marker_pattern = PatternStrings.MARKERS, showLabel=False)
        pw.plotConfig(length = 8000, yoffset = 0, yrange = 1)
        self.view.set_xslider( min_zoom = 0, max_zoom = 0.975, zoom_set = 0.2)
        self.view.set_yslider( min_zoom = 0.01, max_zoom = 5, zoom_set = 1)

        pw.start(name = 'arousal_plot')
        self._plots.append(pw)
        
    def clear_processor_buffers(self):
        for processor in self.model.processors:
            processor.clear_buffers()
            
    def stop_fft_processors(self):
        for processor in self.model.processors:
            if isinstance(processor, FFTAnalyzer):
                processor.stop()
                processor.clear_buffers()
        
    def start_fft_processors(self):
        for i, processor in enumerate(self.model.processors):
            if isinstance(processor, FFTAnalyzer):
                processor.resetBuffers()
                processor.start(name = 'fft-%d' % i)
        
    def update_fft(self, freqbands, patterns):
        for processor in self.model.processors:
            if isinstance(processor, FFTAnalyzer):
                processor.setFreqBands(freqbands)
                processor.setPatterns(patterns)
    
    def stop_fir_filters_processors(self):
        for processor in self.model.processors:
            if isinstance(processor, FIRFilter):
                processor.stop()
                processor.clear_buffers()
                
    def start_fir_filters_processors(self):
        for i, processor in enumerate(self.model.processors):
            if isinstance(processor, FIRFilter):
                processor.start(name = 'fir-%d' % i)
                
    def stop_arousal_processors(self):
        for processor in self.model.processors:
            if isinstance(processor, ArousalProcessor):
                processor.stop()
    
    def start_arousal_processors(self):
        for i, processor in enumerate(self.model.processors):
            if isinstance(processor, ArousalProcessor):
                processor.start(name = 'arousal-%d' % i)
                
    def update_arousal_processors(self, calc_type):
        for processor in self.model.processors:
            if isinstance(processor, ArousalProcessor):
                processor.set_calculation_type(calc_type)
                
    def stop_and_clean_osc_writers(self):
        for processor in self.model.oscwriters:
            if isinstance(processor, OscWriter):
                processor.stop()
                processor.clear_buffers()
        self.model.oscwriters = []
    
    def toggle_playback(self):
        """
        Play or pause all active simulators (streaming data from record-files)
        """
        sim_state = self.model.get_simulation_state()
        
        if sim_state == DataSimulator.PLAYING:
            self.model.pause_simulation()
            self.logger.log(logging.INFO, (__file__, ": applicationcontroller.py: The simulation was paused"))
        else:
            if sim_state == DataSimulator.IDLE:
                for p in self._plots:
                    p.reset()
                    p.clear_buffers()
                    
                self.clear_processor_buffers()
                
                self.set_playback_time(self.view.plot_scrollbar.get())
            
            self.model.start_simulation()
    
    def stop_playback(self):
        self.model.stop_simulation()
        self.view.plot_scrollbar.set(0)
    
    def toggle_play_loopmode(self):
        self.logger.log(logging.INFO, (__file__, ": applicationcontroller.py: Play loopmode:", self.play_loopmode.get()))

    def toggle_headset_connection(self):
#        if self.model.is_headset_connected():
#            self.model.stop_headsets()
#            self.model.disconnect_headsets()
#            self.set_status_text('Disconnected')
#        else:
#            self.view.btn_connect.config(state = 'disabled')
#            self.view.root.update()
#            self.view.canvas.draw()
#            self.connect_headsets()
#            self.view.btn_connect.config(state = 'enabled')

        self.view.btn_connect.config(state = 'disabled')
        self.view.root.update()
        self.view.canvas.draw()
        if self._useMuse:
            self.connect_museheadsets()
        else:
            self.connect_headsets()
        self.view.btn_connect.config(state = 'enabled')

        self.notify()

    def connect_museheadsets(self):
        self.set_status_text('Receiving from Muse Direct')
        self.view.root.update()
        self.model.add_muse_headset_connection()

    def connect_headsets(self):
        if Testing.SERIAL_SIMULATOR:
            self.set_status_text('Connecting to serial simulator ...')
            self.view.root.update()
            try:
                socket = SerialSocket(Testing.SERIAL_PORT)
                if self.model.set_headset_connection(0, socket):
                    self.set_status_text('Connected')
                    self.view.root.update()
                else:
                    self.set_status_text('Connection failed!')
                    self.view.root.update()
            except Exception as e:
                self.logger.log(logging.ERROR, (__file__, ": Connection failed. Exception = ", e))
                self.set_status_text('Connection failed!')
                self.view.root.update()
        else:
            self.set_status_text('Searching for headset(s) ...')
            self.view.root.update()
            
            bt_object = Bluetooth()
            
            try:
                bt_devices = bt_object.findDevices()
            except Exception as e:
                self.set_status_text('No headsets found!')
                self.logger.log(logging.ERROR, (__file__, ": No headsets found. Exception = ", e))
                return
            
            hs_addr = []
            for addr in bt_devices:
                # NOTE: Filter set on host-address i.s.o. host-name ('Wireless EEG' in name) because name
                #       is not always found within search duration (on Windows-8 EEG-kiss laptop).
                 if ('00:06:66' in addr and self._useMuse) or ('00:13:43' in addr and not self._useMuse):
                    hs_addr.append(addr)
            
            if len(hs_addr) == 0:
                
                print 'No EEG-headsets found!'
                self.set_status_text('No headsets found!')
            else:
                print '\rEEG-headsets:', hs_addr
                self.set_status_text('Found %d headset(s)' % len(hs_addr))
                self.view.root.update()
                sleep(1)
                
                count = 0
                for i, addr in enumerate(hs_addr):
                    self.set_status_text('Connecting to headset %d ...' % (i + 1))
                    self.view.root.update()
                    services = bt_object.findServices(addr)
                    if len(services) > 0:
                        socket = bt_object.connectClient_RFCOMM(services)
                        if self.model.set_headset_connection(i, socket):
                            count += 1
                        else:
                            self.set_status_text('Connection failed for headset %d !' % (i + 1))
                            self.view.root.update()
                            sleep(2)
                    else:
                        self.set_status_text('No services found on headset %d !' % (i + 1))
                        self.view.root.update()
                        sleep(2)
                
                self.set_status_text('Connected %d headset(s)' % count)
                self.view.root.update()
    
    def toggle_streaming(self):
        """
        Play or pause all headsets
        """
        if self.model.is_headset_streaming():
            self.model.stop_headsets()
            self.time_controller.stop()
        else:
            for p in self._plots:
                p.reset()
                p.clear_buffers()
                
            self.clear_processor_buffers()
            
            if not self.model.is_headset_serial_busy():
                self.model.start_headsets()
                self.model.send_get_battery_commands()
                self.time_controller.start(name='time_controller')
    
    def toggle_recording(self):
        """
        Starts or stops data recording.
        On stop, data is stored to files
        """
        for index in range( self.model.nr_of_headsets ):
            self.model.set_filename(index, self.view._filename_vars[index].get() )
        if self.model.is_recording():
            self.model.stop_recording()
            self.view.b_toggle_recording.config( text ='Start recording')
            time = self.model.get_headset_time()
            self.logger.log(logging.INFO, (__file__, ": applicationcontroller.py: Stop recording: ", time))
            self.model.blackboard.put_data(PatternStrings.MARKERS, Markers.REC_STOP, time)
        else:
            time = self.model.get_headset_time()
            self.model.start_recording(time)
            self.view.b_toggle_recording.config( text ='Stop recording' )
            self.logger.log(logging.INFO, (__file__, ": applicationcontroller.py: Start recording: ", time))
            self.model.blackboard.put_data(PatternStrings.MARKERS, Markers.REC_START, time)
            self.model.set_foldername()
        
    def ask_quit( self ):
        """ 
        Called on close and close all threads
        """
        if True:
            self.model.stop_simulation()
            self.model.stop_headsets()
            self._running = False
            self.view.root.destroy()

    def clear_filename( self, index ):
        """
        Clears the loaded simulation files
        """
        self.model.simulators[index].clear_data()
        self.view._simulate_filenames[ index ] = 'No file selected'
        self.view.plot_scrollbar.set(0)
        self.notify()
           
    #TODO: Move these to application model      
    def file_open( self, index=0 ):
        """
        Open the selected file (load filename for processing) 
        """
        _eeg_type = 1   # Gefilterde data ( notch + lpf )
        _eega_type = 2  # Ongefilterde data
        
        # Options for opening or saving a file
        root_dir = os.path.relpath( '..\\..\\data\\' )

        file_opt                    = options = {}
        options['defaultextension'] = '.h5'
        options['filetypes']        = [('HDF5 files', '.hdf5'),('All files', '*.*')]
        options['initialdir']       = root_dir
        options['title']            = 'Select a recorded EEG file'

        _file_path_string = tkFileDialog.askopenfilename( **file_opt )
    
        # return if no file was selected (Cancel or Esc pressed)
        if len( _file_path_string ) <= 0:
            return
        
        self.view._simulate_filenames[ index ] = _file_path_string
        
        # Initialize data reader
        reader = HDFReader();
        
        # Reading two datafiles
        try:
            # Read data from selected file
            [ mat, frequencies, markers ] = reader.read( _file_path_string )

            _data = []
            # Get data from 4 channels and create simulator for given index
            for i in self.model.channels:
                try:
                    # Files with timestamps
                    chan_data = [ v[:2] for v in mat[i-1][ _eega_type ] ]
                    self.model.simulators[index] = TimedSimulator( self.model.simulators[index], marker_pattern = PatternStrings.MARKERS )
                except Exception as e:
                    # Files without timestamps
                    chan_data = [ v for v in mat[i-1][ _eega_type ] ]
                    self.model.simulators[index] = DataSimulator( self.model.simulators[index] )
                _data.append(chan_data)
            
#             if markers.any():
            if markers != None:
                _data.append( markers )
            
            # Get simulator patterns
            _eeg_chans = [(PatternStrings.SIGNAL_EEG + '%d' % (index) + PatternStrings.CHANNEL + '%d' % (i))
                            for i in self.model.channels]
            
#             if markers.any():
            if markers != None: # TODO: Check why .any is not working, because now a 'FutureWarning' is raised.
                _eeg_chans.append(PatternStrings.MARKERS)
            
            _interval = 1. / frequencies[_eeg_type]
            self.model.simulators[index].set_simulation_data(_data)
            self.model.simulators[index].set_simulation_interval(_interval)
            self.model.simulators[index].set_patterns(_eeg_chans)
            
        except IOError as e:
            self.logger.log(logging.ERROR, (__file__, ": IOError = ", e))
        except ValueError as e:
            self.logger.log(logging.ERROR, (__file__, ": ValueError = ", e))
        except TypeError as e:
            self.logger.log(logging.ERROR, (__file__, ": TypeError = ", e))
            self.clear_filename(index)
            
        self.notify()
                
    def select_mode_simulating(self):
        """
        Switch GUI to simulation mode
        """
        self.view.streamPanel.pack_forget()
        self.view.simPanel.pack()
        self.view.plotscroll_panel.pack( side='bottom', fill='x', padx=10 )
        self.notify()
    
    def select_mode_streaming(self):
        """
        Switch GUI to streaming mode
        """
        self.view.simPanel.pack_forget()
        self.view.streamPanel.pack(anchor='w')
        self.view.plotscroll_panel.pack_forget()
        self.notify()
    
    def show_display_settings(self):
        '''
        Shows the settings dialog of the right type
        '''
        print 'Show settings for: ' + self.view.cb_display_value.get()
        
        if self.view.cb_display_value.get() == VisualisationTypes.TIME:
            self.cp = self.model.timeSettings.getCopy()
            self.view.show_settings_time(self.cp)
        elif self.view.cb_display_value.get() == VisualisationTypes.FREQUENCY:
            self.cp = self.model.frequencySpectrumSettings.getCopy()
            self.view.show_settings_frequency(self.cp)
        elif self.view.cb_display_value.get() == VisualisationTypes.FREQUENCY_BAND:
            self.cp = self.model.frequencyBandSettings.getCopy()
            self.view.show_settings_frequency_band(self.cp)
        elif self.view.cb_display_value.get() == VisualisationTypes.AROUSEL:
            self.view.show_settings_arousel()
        elif self.view.cb_display_value.get() == VisualisationTypes.VALENCE:
            self.view.show_settings_valence()
            
    def save_settings(self, arg):
        if isinstance(arg, TimeSettings):
            self.model.timeSettings.update(arg)
            self.re_init_time_plot()
        elif isinstance(arg, SpectrumSettings):
            self.model.frequencySpectrumSettings.update(arg)
            self.re_init_frequency_spectrum_plot()
        elif isinstance(arg, FrequencyBandSettings):
            self.model.frequencyBandSettings.update(arg)
            self.re_init_freqency_band_plot()
        # TODO: Add more setting instances to save
        else:
            self.logger.log(logging.WARNING, (__file__, ": No instance found to save."))
            
    def visualisationTypeChanged(self, event):
        '''
        Method is called when the selected display mode is changed
        '''
        #Close setting if open
        self.view.remove_settings_screen()
        
        for p in self._plots:
            p.reset()
            p.clear_buffers()
        self.clear_processor_buffers()

        if self.view.cb_display_value.get() == VisualisationTypes.TIME:
            self.re_init_time_plot()
        elif self.view.cb_display_value.get() == VisualisationTypes.FREQUENCY:
            self.re_init_frequency_spectrum_plot()
        elif self.view.cb_display_value.get() == VisualisationTypes.FREQUENCY_BAND:
            self.re_init_freqency_band_plot()
        elif self.view.cb_display_value.get() == VisualisationTypes.AROUSEL:
            self.re_init_arousal_plot()
        elif self.view.cb_display_value.get() == VisualisationTypes.VALENCE:
            self.re_init_valence_plot()
            
        self.logger.log(logging.INFO, (__file__, ": Settings changed to: ", self.view.cb_display_value.get()))
        
    def re_init_time_plot(self):
        self.stop_fft_processors()
        self.start_fir_filters_processors()
        self.stop_arousal_processors()
        self.view.init_plot_panel(self.view._frame, len(self.model.get_active_channels(VisualisationTypes.TIME)))
        self.stop_and_clean_osc_writers()
        self.initialize_time_plots()
        self.view.start()
        
    def re_init_freqency_band_plot(self):
        self.stop_fir_filters_processors()
        pats=[]
        for _, channel in enumerate(self.model.get_active_channels(VisualisationTypes.FREQUENCY_BAND)):
            for headset in range(self.model.nr_of_headsets):
                pats.append(PatternStrings.SIGNAL_EEG + '%d' % (headset) + PatternStrings.CHANNEL + '%d' % (channel))
        self.update_fft( self.model.frequencyBandSettings.frequencyBand.get(), pats )
        self.start_fft_processors()
        self.stop_arousal_processors()
        self.view.init_plot_panel(self.view._frame, len(self.model.get_active_channels(VisualisationTypes.FREQUENCY_BAND)))
        self.stop_and_clean_osc_writers()
        self.initialize_frequency_band_plots()
        self.view.start()
        
    def re_init_frequency_spectrum_plot(self):
        self.start_fir_filters_processors()
        pats = []
        for _, channel in enumerate(self.model.get_active_channels(VisualisationTypes.FREQUENCY)):
            for headset in range(self.model.nr_of_headsets):
                pats.append(PatternStrings.SIGNAL_EEG + '%d' % (headset) + PatternStrings.CHANNEL + '%d' % (channel) + PatternStrings.FILTERNOTCH + PatternStrings.FILTERLPF)
        self.update_fft( [], pats)
        self.start_fft_processors()
        self.stop_arousal_processors()
        self.view.init_plot_panel(self.view._frame, len(self.model.get_active_channels(VisualisationTypes.FREQUENCY)))
        self.stop_and_clean_osc_writers()
        self.initialize_frequency_spectrum_plots()
        self.view.start()
        
    def re_init_arousal_plot(self):
        self.stop_fir_filters_processors()
        pats = []
        for channel in [1,3]:
            for headset in range(self.model.nr_of_headsets):
                pats.append(PatternStrings.SIGNAL_EEG + '%d' % (headset) + PatternStrings.CHANNEL + '%d' % (channel))
        self.update_fft( [FrequencyBands.ALPHA, FrequencyBands.BETA], pats)
        self.start_fft_processors()
        self.update_arousal_processors(type=VisualisationTypes.AROUSEL)
        self.start_arousal_processors()
        self.view.init_plot_panel(self.view._frame, 1)
        self.stop_and_clean_osc_writers()
        self.initialize_arousal_plot()
        self.view.start()
        
    def re_init_valence_plot(self):
        self.stop_fir_filters_processors()
        pats = []
        for channel in [1,3]:
            for headset in range(self.model.nr_of_headsets):
                pats.append(PatternStrings.SIGNAL_EEG + '%d' % (headset) + PatternStrings.CHANNEL + '%d' % (channel))
        self.update_fft( [FrequencyBands.ALPHA, FrequencyBands.BETA], pats)
        self.start_fft_processors()
        self.update_arousal_processors(type=VisualisationTypes.VALENCE)
        self.start_arousal_processors()
        self.view.init_plot_panel(self.view._frame, 1)
        self.stop_and_clean_osc_writers()
        #Is the same as arousal, maybe create separate if other zoom/plotconfig is needed
        self.initialize_arousal_plot()
        self.view.start()

    def set_status_text( self, newStatus ):
        """
        Sets status text in the status bar
        """
        self.view.statusText.config( text = newStatus )
        self.notify()
    
    def set_gui_mode_active(self, active):        
        state = 'enabled' if active else 'disabled'
        self.view.rb_sim.configure( state = state )
        self.view.rb_stream.configure( state = state )
        
        for i in range(self.model.nr_of_headsets):
            self.view.simfiles[i].configure( state = state )
            self.view.browse_buttons[i].configure( state = state )
#             if self.view.com_selections[i]:
#                 newState = 'disabled'
#                 if state is 'enabled':
#                     # don't use "enable" on a comboBox: it allows the user to change the entries
#                     newState = 'readonly'
#                 self.view.com_selections[i].configure( state = newState )
                
    # TODO: Refactor this monster    
    def check_gui_state(self):
        if self._running:
            is_receiving = self.model.is_receiving_data()
            
            self.set_gui_mode_active( not is_receiving )
            
            # Update widgets config
            self.update_gui_widgets_config()
                 
            # simulation file clear buttons
            for sim, but in zip(self.model.simulators, self.view.clear_buttons ):
                if sim and sim.is_data_set() and sim.get_simulation_state() is DataSimulator.IDLE:
                    but.configure( state = 'enabled' )
                    to = self.model.get_simulation_length()
                    self.view.plot_scrollbar.configure( to = to )
                else:
                    but.configure( state = 'disabled' )
                    
            sim_state = self.model.get_simulation_state()
            
            if sim_state == DataSimulator.IDLE:
                self.view.b_toggle_simulation.configure( text = 'Play' )
                self.view.b_stop_simulation.configure( state = 'disabled' )
            else:
                if sim_state == DataSimulator.PAUSED:
                    self.view.b_toggle_simulation.config( text = 'Play' )
                if sim_state == DataSimulator.PLAYING:
                    self.view.b_toggle_simulation.configure( text = 'Pause' )
                self.view.b_stop_simulation.configure( state = 'enabled' )
                
            all_files_selected = all( [s == 'No file selected' for s in self.view._simulate_filenames] )
            self.view.b_toggle_simulation.configure( state = 'disabled' if all_files_selected else 'enabled' )
            self.view.plot_scrollbar.configure( state = 'disabled' if all_files_selected else 'normal' )
                
            for i in range(self.model.nr_of_headsets):    
                self.view.simfiles[i].configure( text = self.view._simulate_filenames[i] )
         
    def update_gui_widgets_config(self):
        '''
            Update the config of the widgets 
        '''
        # Determine if headset is connected and update gui accordingly
        hs_connected = self.model.is_headset_connected()
         
        self.view.btn_connect.config( text = 'Disconnect' if hs_connected else 'Connect' )
        self.view.b_toggle_streaming.config( state = 'enabled' if hs_connected else 'disabled' )
        
        # Determine if headset is streaming and update gui accordingly 
        is_streaming = self.model.is_headset_streaming()
        
        if is_streaming:
            if hs_connected:
                self.view.btn_connect.config(state = 'disabled')
                
            self.view.b_toggle_recording.config( state = 'enabled' )
            self.view.b_toggle_streaming.config( text ='Stop streaming')
        else:
            if hs_connected:
                self.view.btn_connect.config(state = 'enabled')
                
            self.view.b_toggle_recording.config( state = 'disabled' )
            self.view.b_toggle_streaming.config( text ='Start streaming')

        # Determine if headset is being recorded and update gui accordingly
        is_rec = self.model.is_recording()
        
        if is_rec:
            self.view.b_toggle_streaming.config( state = 'disabled' )

        self.view.b_toggle_recording.config( text = 'Stop recording' if is_rec else 'Start recording' )
        
        # Determine the gui state for widgets
        gui_state = 'enabled' if is_rec else 'disabled'
                    
        self.view.b_poi.config( state = gui_state )
        self.view.b_start_kiss.config( state = gui_state )
        self.view.b_stop_kiss.config( state = gui_state )        
            
    def update_battery_levels(self):
        """
        Get battery levels from headsets and present them in the GUI
        """
        for hs, view in zip(self.model.headsets,[self.view.battIndication1, self.view.battIndication2]):
            if hs.is_streaming():
                bat = hs.get_battery()
                view.config(text = 'Battery: %d%%' % (bat) if bat > 0 else '                 -')
            
    def clear_battery_levels(self):
        """
        Clear headset battery levels presented in the GUI
        """
        for hs, view in zip(self.model.headsets,[self.view.battIndication1, self.view.battIndication2]):
            if not hs.is_streaming():
                view.config(text = '                 -')
            
    def update_time(self):
        """
        Get headset or simulation time and present it in the GUI
        """
        # TODO: Declare global state-var mode-selection (MODE_HEADSET, MODE_PLAYBACK)
        time = None
        if self.model.is_headset_streaming():
            time = self.model.get_headset_time()
        else:
            if self.model.get_simulation_state() == DataSimulator.PLAYING:
                time = self.model.get_simulation_time()
                self.view.plot_scrollbar.set( time )
        
        if time != None:
            for pw in self._plots:
                pw.plotConfig( xUpper=time )
    
    ### Observer component ###
    def notify(self, message=None, arg=None):
        """
        Overrides the Observer notify
        Implements different actions for different messages
        Default action is to update all GUI components
        """
        if message:
            if message is 'stop_streaming':
                self.clear_battery_levels()
            elif message is 'stop_playback':  # One of the simulators has stopped
                self.stop_playback()          # Now stop all simulators
                if self.play_loopmode.get():
                    self._restartPlayback = True
            elif message is 'battery':
                self.update_battery_levels()
                return
            elif message is 'update_time':
                self.update_time()
                return
            elif message is 'save_settings':
                self.save_settings(arg)
                return
            elif message is 'key_event':
                self.handle_key_event(arg)
                return

        self.check_gui_state()

    def handle_key_event(self, key):
        if key == '\x12': # ctrl + r
            self.toggle_recording()
        elif self.model.is_recording():
            if key == '\x0b': # ctrl + k
                if not self._kissing:
                    self.start_kiss_marker()
                else:
                    self.stop_kiss_marker()
            elif key == '\x10': # ctrl + p
                self.poi_marker()
        pass
    