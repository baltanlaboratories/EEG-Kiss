'''
Created on 23 apr. 2015

@author: Bas.Kooiker
'''
import logging
import os

import Tkinter                          as tk
import ttk                              as ttk 
import matplotlib.pyplot                as plt

from sys                                import platform as _platform
from matplotlib.transforms              import Bbox
from matplotlib.backends.backend_tkagg  import FigureCanvasTkAgg
from root.core.observerpattern          import Subject
from root.version                       import Version
from root.core.constants                import VisualisationTypes, ChannelTypes, FrequencyBands
from Tkconstants                        import HORIZONTAL, BOTH, LEFT, RIGHT, NW, SE
from Tkinter                            import StringVar
from functools                          import partial

class ApplicationView( Subject ):    
    """
    This ApplicationView is the view component of the MVC pattern.
    All view components are created using the ttk library
    """
    
    def __init__(self): 
        Subject.__init__( self ) 
        
        self.logger = logging.getLogger()
        
        width  = 1200
        height = 600
        self.nr_of_channels = 2     # TODO: Rename this to something like 'max_nr_of_signals_per_channel'
        self.colors         = ['white','yellow', 'red']
        
        self.root = tk.Tk( 'EEG KISS' )
        self.root.resizable(width=True, height=True)
        self.root.minsize(width=800, height=450)
        self.root.wm_geometry( "%dx%d" % (width, height) )
        self.root.state('zoomed')
        
        self.root.wm_title( "EEG_Kiss - versie " + Version().getVersionNumber() )
        
        #TODO Turn this line off when exporting with py2exe
        self.root.wm_iconbitmap(bitmap = os.path.dirname(__file__) + "\..\..\icons\EEG_Kiss_icon.ico")
    
        self.set_theme_style()
    
        screen_width    = self.root.winfo_screenwidth()
        screen_height   = self.root.winfo_screenheight()
        
        self._frame     = ttk.Frame( self.root, width=screen_width, height=screen_height )
        self._frame.pack_propagate( False )
        self._frame.pack( )
        
        self.settings_sreen = None
        
        self.init_plot_panel(self._frame)
        self.init_mode_panel(self._frame)
        self.init_config_panel(self._frame)
        self.init_simulation_panel(self._frame)
        self.init_streaming_panel(self._frame)
    
        self.root.bind("<Key>", self.key, False)
    
    def key(self, event):
        print 'Key pressed:', repr(event.char)
        self.notify_observers("key_event", event.char)
    
    def set_theme_style(self):
        style = ttk.Style()
        
        if _platform == "linux" or _platform == "linux2":
            # linux
            style.theme_use('classic') 
        elif _platform == "darwin":
            # MAC OS X
            style.theme_use('aqua') 
        elif _platform == "win32":
            # Windows
            style.theme_use('xpnative')         
        
    def init_plot_panel(self,frame,number_of_plots=4): 
        nr_of_plots = number_of_plots
        
        self.logger.log(logging.INFO, (__file__, ": Change number of plots to: ", number_of_plots))
        
        if not hasattr(self, 'plot_panel'):
            self.plot_panel = ttk.Frame( master=frame )
            self.plot_panel.pack( side='top', fill=BOTH, expand=True )
            self.fig = plt.Figure( figsize=(1,1), dpi=100 )
            self.fig.set_facecolor('black')
    
        self.fig.clear()
        
        if nr_of_plots > 1:
            self._fig, axes = plt.subplots( nr_of_plots )
            
            for index, ax in enumerate(axes):
                y = (index)/(nr_of_plots*1.0)
                position = [ [0, y], [1, y+.985/nr_of_plots] ]
                ax.set_position( Bbox(position) )
                
            self._axes = axes.tolist()
            self._axes.reverse()
        elif nr_of_plots == 1:
            self._fig, ax = plt.subplots( 1 )
            ax.set_position( Bbox([ [0, 0], [1, 1] ]) )
            self._axes = [ax]
            self._axes.reverse()
        else:
            self._fig = None
            self._axes = []
        
        if not hasattr(self, 'plotscroll_panel'):
            
            self.plotscroll_panel   = ttk.Frame( master = self.plot_panel )
            self.plot_scrollbar     = tk.Scale( master=self.plotscroll_panel, orient=HORIZONTAL )
            
            self.plot_scrollbar.pack( side='bottom', fill='x' )
     
    def init_mode_panel(self, frame):
        # Toggle between streaming and simulating
        modePanel = ttk.Frame( master=frame )
        modePanel.pack( side='left' )

        ttk.Frame( master=modePanel, width=10 ).grid( row=0, rowspan=2, column=0 )

        ttk.Label( master=modePanel, text='Input Modus: ' ).grid( row=0, column=1, sticky='w' )
        
        self.rb_sim     = ttk.Radiobutton( master=modePanel, text='Files', variable='Mode', value='sim' )
        self.rb_stream  = ttk.Radiobutton( master=modePanel, text='Headsets', variable='Mode', value='stream' )
        
        self.rb_sim.grid( row=0, column=2 )
        self.rb_stream.grid( row=0, column=3 )
        
        # Select the visualisation type
        ttk.Label( master=modePanel, text='Display Modus: ' ).grid( row=1, column=1, sticky='w' )
        self.cb_display_value       = StringVar()
        self.cb_display             = ttk.Combobox(master=modePanel, textvariable=self.cb_display_value, state='readonly')
        self.cb_display['values']   = (VisualisationTypes.TIME, VisualisationTypes.FREQUENCY, VisualisationTypes.FREQUENCY_BAND, VisualisationTypes.AROUSEL, VisualisationTypes.VALENCE)
        self.cb_display.current(0)
        self.cb_display.grid(row=1, column=2)
        
        self.b_display_settings = ttk.Button( master=modePanel, text='Settings...' )
        self.b_display_settings.grid(row=1, column=3)
    
    def init_config_panel(self, frame):
        self.config_panel = ttk.Frame(master=frame)
        
#         self.statusText = ttk.Label(master=self.config_panel, text="Idle")
#         self.statusText.grid(rowspan=2)#, columnspan=3, sticky='w')
#         ttk.Frame(master=self.config_panel, width=50).grid(column=3, rowspan=2)
        
        self.zoom_sliders = []
        labels = ["Horizontal scale", "Vertical scale"]
        for i in range(2):
            ttk.Label(master=self.config_panel, text=labels[i], anchor='w').grid(row=i, column=4, sticky='e')
            self.zoom_sliders.append(ttk.Scale(master=self.config_panel, orient=HORIZONTAL))
            self.zoom_sliders[i].grid(row=i, column=5, padx=10)
        
        self.zoom_sliders[0].config( from_=0, to=0.975 )
        self.zoom_sliders[0].set( 0.2 )

        # TODO: Use constants for default yoffset and yrange values
        self.zoom_sliders[1].config( from_=12000, to=1000 )
        self.zoom_sliders[1].set( 4000 )
        
        self.config_panel.pack(side='right')
    
    def init_simulation_panel(self, frame):
        self.simPanel = ttk.Frame( master=frame )
        # filenames for data simulating
        self._simulate_filenames = [ tk.StringVar( ) for _ in range(self.nr_of_channels) ]
        for i in range(self.nr_of_channels):
            self._simulate_filenames[i] = 'No file selected'
        
        # File load buttons
        self.simfiles       = [ None for _ in range(self.nr_of_channels) ]
        self.browse_buttons = [ None for _ in range(self.nr_of_channels) ]
        self.clear_buttons  = [ None for _ in range(self.nr_of_channels) ]
        
        for i in range(self.nr_of_channels):
            ttk.Label( master=self.simPanel, text='File %d: '%(i+1), background=self.colors[i] ).grid( row=i, column=0 )
            self.simfiles[i]        = ttk.Label( master=self.simPanel, text=self._simulate_filenames[0], relief = 'sunken', width = 75 )            
            self.browse_buttons[i]  = ttk.Button( master=self.simPanel, text='Browse...' )
            self.clear_buttons[i]   = ttk.Button( master=self.simPanel, text='Clear' )
            
            self.simfiles[i].grid( row=i, column=1 )
            self.browse_buttons[i].grid( row=i, column=2 )
            self.clear_buttons[i].grid( row=i, column=3 )       

        ttk.Frame( master=self.simPanel, width=50 ).grid( row=0, column=4 )
        
        # Start/pause & stop buttons
        self.b_toggle_simulation = ttk.Button( master=self.simPanel, text='Play' )
        self.b_stop_simulation   = ttk.Button( master=self.simPanel, text='Stop' )
        self.cb_loopmode         = ttk.Checkbutton( master=self.simPanel, text='Loop-mode'  )
        
        self.b_toggle_simulation.grid( row=0, column=5 )
        self.b_stop_simulation.grid( row=1, column=5 )
        self.cb_loopmode.grid( row=0, column=6 )
    
    def init_streaming_panel(self, frame):
        self.streamPanel = ttk.Frame( master=frame )
        self.streamPanel.pack(anchor='w')

        ttk.Frame(master=self.streamPanel, width=150).grid(column=0, row=0, rowspan=2)
        
        # Bluetooth connect button
        self.btn_connect = ttk.Button(master=self.streamPanel, text='Connect')
        self.btn_connect.grid(column=1, row=0, rowspan=2)
        
        ttk.Frame(master=self.streamPanel, width=50).grid(row=0, rowspan=2, column=2)
        
        # Battery-level indication        
        self.battIndication1 = ttk.Label(master = self.streamPanel, text = '                 -', width = 12)
        self.battIndication2 = ttk.Label(master = self.streamPanel, text = '                 -', width = 12)
        
        self.battIndication1.grid(row = 0, column = 3)
        self.battIndication2.grid(row = 1, column = 3)
        
        # Headset labels
        ttk.Label( master=self.streamPanel, text='Headset 1: ', background=self.colors[0] ).grid( row=0, column=4 )
        ttk.Label( master=self.streamPanel, text='Headset 2: ', background=self.colors[1] ).grid( row=1, column=4 )
        
        ttk.Frame( master=self.streamPanel, width=10 ).grid( row=0, rowspan=2, column=5 )
        
        # filenames for data recording
        self._filename_vars = []
        self._filename_vars.append( tk.StringVar(value='filename1') )
        self._filename_vars.append( tk.StringVar(value='filename2') )

        ttk.Label( master=self.streamPanel, text='Save File 1: ' ).grid( row=0, column=6 )
        ttk.Entry( master=self.streamPanel, textvariable=self._filename_vars[0] ).grid( row=0, column=7 )
        
        ttk.Label( master=self.streamPanel, text='Save File 2: ' ).grid( row=1, column=6 )
        ttk.Entry( master=self.streamPanel, textvariable=self._filename_vars[1] ).grid( row=1, column=7 )
        
        ttk.Frame( master=self.streamPanel, width=50 ).grid( row=0, rowspan=2, column=8 )
        
        # Start/Stop streaming button
        self.b_toggle_streaming = ttk.Button( master=self.streamPanel, text='Start Streaming' )
        self.b_toggle_streaming.grid( row=0, column=9 )
        self.b_toggle_streaming.config( state = 'disabled' )
        
        # Start/Stop recording button
        self.b_toggle_recording = ttk.Button( master=self.streamPanel, text='Start Recording' )
        self.b_toggle_recording.grid( row=1, column=9 )
        self.b_toggle_recording.config( state = 'disabled' )
        
        ttk.Frame( master=self.streamPanel, width=20 ).grid( row=0, rowspan=2, column=10 )
        
        self.stream_counter_value = StringVar(value = '-')
        self.stream_counter = ttk.Label(master = self.streamPanel, textvariable = self.stream_counter_value, width = 3)
        self.stream_counter.grid( row=0, column=11, sticky='e' )
        
        self.rec_counter_value = StringVar(value = '-')
        self.rec_counter = ttk.Label(master = self.streamPanel, textvariable = self.rec_counter_value, width = 3)
        self.rec_counter.grid( row=1, column=11, sticky='e' )
        
        ttk.Frame( master=self.streamPanel, width=50 ).grid( row=0, rowspan=2, column=12 )
        
        if True:
            # TODO: Perform this with pointing-device i.s.o. buttons
            # Start kiss button
            self.b_start_kiss = ttk.Button( master=self.streamPanel, text='Start kiss' )
            self.b_start_kiss.grid( row=0, column=13, sticky='we' )
            self.b_start_kiss.config( state = 'disabled' )
             
            # Stop kiss button
            self.b_stop_kiss = ttk.Button( master=self.streamPanel, text='Stop kiss' )
            self.b_stop_kiss.grid( row=0, column=14, sticky='we' )
            self.b_stop_kiss.config( state = 'disabled' )
             
            # Point of interest button
            self.b_poi= ttk.Button( master=self.streamPanel, text='Point of interest' )
            self.b_poi.grid( row=1, column=13, columnspan=2, sticky='we' )
            self.b_poi.config( state = 'disabled' )
        
        ttk.Frame(master=self.streamPanel, width=50).grid(column=15, rowspan=2)
        self.statusText = ttk.Label(master=self.streamPanel, text="Idle")
        self.statusText.grid(row=0, column=16, rowspan=2)
        
        self.rb_stream.invoke()
    
    def start(self):
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
        
        try:
            self.canvas = FigureCanvasTkAgg( self._fig, master=self.plot_panel )
            self.canvas.get_tk_widget().pack( fill=tk.BOTH, expand=1 )
            self.canvas._tkcanvas.config(background="#c0c0c0", borderwidth=1, highlightthickness=0)
            self.canvas.show()
        except Exception as e:
            self.logger.log(logging.ERROR, (__file__, ": Failed to show the canvas: ", e))

    def get_axes(self):
        """
        Returns the PyPlot axes
        """
        return self._axes
    
    def set_xslider(self, min_zoom, max_zoom, zoom_set):
        self.zoom_sliders[0].config( from_ = min_zoom, to = max_zoom )
        self.zoom_sliders[0].set( zoom_set )
    
    def set_yslider(self, min_zoom, max_zoom, zoom_set):
        self.zoom_sliders[1].config( from_ = max_zoom, to = min_zoom )
        self.zoom_sliders[1].set( zoom_set )
    
    def show_settings_time(self, timeSettings=None):
        if self.settings_sreen == None:
            self.create_settings_screen(VisualisationTypes.TIME,300,220)
            
            titleChannels = tk.Label(self.settings_sreen, text="Displayed channels:")
            titleChannels.pack(anchor=NW, padx=20, pady=10)
            
            frame1 = tk.Frame(self.settings_sreen)
            frame1.pack(side="top", fill="x", padx=20)
            
            checkLeft = ttk.Checkbutton(self.settings_sreen, text=ChannelTypes.LEFT, variable=timeSettings.channel[ChannelTypes.LEFT])
            checkLeft.pack(in_=frame1, side=LEFT)    
            
            checkRight = ttk.Checkbutton(self.settings_sreen, text=ChannelTypes.RIGHT, variable=timeSettings.channel[ChannelTypes.RIGHT])
            checkRight.pack(in_=frame1, side=LEFT, padx=37)
            
            frame2 = ttk.Frame(self.settings_sreen)
            frame2.pack(side="top", fill="x", padx=20)
            
            checkFront = ttk.Checkbutton(self.settings_sreen, text=ChannelTypes.MID, variable=timeSettings.channel[ChannelTypes.MID])
            checkFront.pack(in_=frame2, side=LEFT)
            
            checkBack = ttk.Checkbutton(self.settings_sreen, text=ChannelTypes.BACK, variable=timeSettings.channel[ChannelTypes.BACK])
            checkBack.pack(in_=frame2, side=LEFT, padx=20)
            
            titleLabels = tk.Label(self.settings_sreen, text="Display settings:")
            titleLabels.pack(anchor=NW, padx=20, pady=10)
            
            frame3 = ttk.Frame(self.settings_sreen)
            frame3.pack(side="top", fill="x", padx=20)
            
            checkLabels = ttk.Checkbutton(self.settings_sreen, text='Show labels on plot', variable=timeSettings.showLabels)
            checkLabels.pack(in_=frame3, side=LEFT)
            
            buttonFrame = ttk.Frame(self.settings_sreen)
            buttonFrame.pack(anchor=SE, fill="x", padx=20, pady=20)
            
            button = ttk.Button(self.settings_sreen, text="Cancel", command=self.remove_settings_screen)
            button.pack(in_=buttonFrame, side=RIGHT)
            
            button = ttk.Button(self.settings_sreen, text="Ok", command=partial(self.save_settings_screen, timeSettings))
            button.pack(in_=buttonFrame, side=RIGHT, padx=10)
        else:
            if self.settings_sreen.type==VisualisationTypes.TIME:
                self.settings_sreen.focus()
            else:
                self.remove_settings_screen()
                self.show_settings_time(timeSettings)
        
    def show_settings_frequency(self, frequencySettings=None, specificSettings=None):
        if self.settings_sreen == None:
            self.create_settings_screen(VisualisationTypes.FREQUENCY,300,220)
            
            titleChannels = tk.Label(self.settings_sreen, text="Displayed channels:")
            titleChannels.pack(anchor=NW, padx=20, pady=10)
            
            frame1 = tk.Frame(self.settings_sreen)
            frame1.pack(side="top", fill="x", padx=20)
            
            checkLeft = ttk.Checkbutton(self.settings_sreen, text=ChannelTypes.LEFT, variable=frequencySettings.channel[ChannelTypes.LEFT])
            checkLeft.pack(in_=frame1, side=LEFT)
                
            checkRight = ttk.Checkbutton(self.settings_sreen, text=ChannelTypes.RIGHT, variable=frequencySettings.channel[ChannelTypes.RIGHT])
            checkRight.pack(in_=frame1, side=LEFT, padx=37)
            
            frame2 = ttk.Frame(self.settings_sreen)
            frame2.pack(side="top", fill="x", padx=20)
            
            checkFront = ttk.Checkbutton(self.settings_sreen, text=ChannelTypes.MID, variable=frequencySettings.channel[ChannelTypes.MID])
            checkFront.pack(in_=frame2, side=LEFT)
            
            checkBack = ttk.Checkbutton(self.settings_sreen, text=ChannelTypes.BACK, variable=frequencySettings.channel[ChannelTypes.BACK])
            checkBack.pack(in_=frame2, side=LEFT, padx=20)
            
            titleLabels = tk.Label(self.settings_sreen, text="Display settings:")
            titleLabels.pack(anchor=NW, padx=20, pady=10)
            
            frame3 = ttk.Frame(self.settings_sreen)
            frame3.pack(side="top", fill="x", padx=20)
            
            checkLabels = ttk.Checkbutton(self.settings_sreen, text='Show labels on plot', variable=frequencySettings.showLabels)
            checkLabels.pack(in_=frame3, side=LEFT)
            
            buttonFrame = ttk.Frame(self.settings_sreen)
            buttonFrame.pack(anchor=SE, fill="x", padx=20, pady=20)
            
            button = ttk.Button(self.settings_sreen, text="Cancel", command=self.remove_settings_screen)
            button.pack(in_=buttonFrame, side=RIGHT)
            
            button = ttk.Button(self.settings_sreen, text="Ok", command=partial(self.save_settings_screen, frequencySettings))
            button.pack(in_=buttonFrame, side=RIGHT, padx=10)
        else:
            if self.settings_sreen.type==VisualisationTypes.FREQUENCY:
                self.settings_sreen.focus()
            else:
                self.remove_settings_screen()
                self.show_settings_frequency(frequencySettings)
    
    def show_settings_frequency_band(self, frequencyBandSettings=None):
        if self.settings_sreen == None:
            self.create_settings_screen(VisualisationTypes.FREQUENCY_BAND, 300, 275 + 21*(len(FrequencyBands.values) - 1))
            
            titleChannels = tk.Label(self.settings_sreen, text="Displayed channels:")
            titleChannels.pack(anchor=NW, padx=20, pady=10)
            
            frame1 = tk.Frame(self.settings_sreen)
            frame1.pack(side="top", fill="x", padx=20)
            
            checkLeft = ttk.Checkbutton(self.settings_sreen, text=ChannelTypes.LEFT, variable=frequencyBandSettings.channel[ChannelTypes.LEFT])
            checkLeft.pack(in_=frame1, side=LEFT)    
            
            checkRight = ttk.Checkbutton(self.settings_sreen, text=ChannelTypes.RIGHT, variable=frequencyBandSettings.channel[ChannelTypes.RIGHT])
            checkRight.pack(in_=frame1, side=LEFT, padx=37)
            
            frame2 = ttk.Frame(self.settings_sreen)
            frame2.pack(side="top", fill="x", padx=20)
            
            checkFront = ttk.Checkbutton(self.settings_sreen, text=ChannelTypes.MID, variable=frequencyBandSettings.channel[ChannelTypes.MID])
            checkFront.pack(in_=frame2, side=LEFT)
            
            checkBack = ttk.Checkbutton(self.settings_sreen, text=ChannelTypes.BACK, variable=frequencyBandSettings.channel[ChannelTypes.BACK])
            checkBack.pack(in_=frame2, side=LEFT, padx=20)
            
            titleLabels = tk.Label(self.settings_sreen, text="Display settings:")
            titleLabels.pack(anchor=NW, padx=20, pady=10)
            
            frame3 = ttk.Frame(self.settings_sreen)
            frame3.pack(side="top", fill="x", padx=20)
            
            checkLabels = ttk.Checkbutton(self.settings_sreen, text='Show labels on plot', variable=frequencyBandSettings.showLabels)
            checkLabels.pack(in_=frame3, side=LEFT)
            
            titleFreqBand = tk.Label(self.settings_sreen, text="Select frequency band:")
            titleFreqBand.pack(anchor=NW, padx=20, pady=10)
            
            for band in FrequencyBands.values:
                b = ttk.Radiobutton(self.settings_sreen, text=band, variable=frequencyBandSettings.frequencyBand, value=band)
                b.pack(anchor=NW, padx=20)
            
            buttonFrame = ttk.Frame(self.settings_sreen)
            buttonFrame.pack(anchor=SE, fill="x", padx=20, pady=20)
            
            button = ttk.Button(self.settings_sreen, text="Cancel", command=self.remove_settings_screen)
            button.pack(in_=buttonFrame, side=RIGHT)
            
            button = ttk.Button(self.settings_sreen, text="Ok", command=partial(self.save_settings_screen, frequencyBandSettings))
            button.pack(in_=buttonFrame, side=RIGHT, padx=10)
        else:
            if self.settings_sreen.type==VisualisationTypes.FREQUENCY_BAND:
                self.settings_sreen.focus()
            else:
                self.remove_settings_screen()
                self.show_settings_frequency_band(frequencyBandSettings)
    
    def show_settings_arousel(self, arousalSettings=None):
        if self.settings_sreen == None:
            self.create_settings_screen(VisualisationTypes.AROUSEL,200,100)
            
            label = tk.Label(self.settings_sreen, text="There are no settings available")
            label.pack(pady=15)
            
            button = tk.Button(self.settings_sreen, text="Close", command=self.remove_settings_screen)
            button.pack()
        else:
            if self.settings_sreen.type==VisualisationTypes.AROUSEL:
                self.settings_sreen.focus()
            else:
                self.remove_settings_screen()
                self.show_settings_arousel(arousalSettings)
    
    def show_settings_valence(self, valenceSettings=None):
        if self.settings_sreen == None:
            self.create_settings_screen(VisualisationTypes.VALENCE,200,100)
            
            label = tk.Label(self.settings_sreen, text="There are no settings available")
            label.pack(pady=15)
            
            button = tk.Button(self.settings_sreen, text="Close", command=self.remove_settings_screen)
            button.pack()
        else:
            if self.settings_sreen.type==VisualisationTypes.VALENCE:
                self.settings_sreen.focus()
            else:
                self.remove_settings_screen()
                self.show_settings_valence(valenceSettings)
        
    def remove_settings_screen(self):
        if self.settings_sreen != None:
            self.settings_sreen.destroy()
            self.settings_sreen=None
            
    def save_settings_screen(self, settings):
        self.notify_observers("save_settings", settings)
        self.remove_settings_screen()
            
    def create_settings_screen(self, title, width=300, height=200):
        self.settings_sreen = tk.Toplevel(self.root)
        self.settings_sreen.type = title
        self.settings_sreen.title("Settings - " + title)
        self.settings_sreen.protocol("WM_DELETE_WINDOW", self.remove_settings_screen)
        self.settings_sreen.resizable(width=False, height=False)
        
        ws = self.settings_sreen.winfo_screenwidth()    #This value is the width of the screen
        hs = self.settings_sreen.winfo_screenheight()   #This is the height of the screen
        
        # calculate position x, y
        x = (ws/2) - (width/2)
        y = (hs/2) - (height/2)
        
        #This is responsible for setting the dimensions of the screen and where it is placed
        self.settings_sreen.wm_geometry( "%dx%d+%d+%d" % (width, height, x, y) )
