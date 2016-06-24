
import time
from random import randint
from root.core.dataconsumer import DataConsumer
from root.core.constants import PatternStrings


def random_filenames():
    return 'newfile_' + str(time.time()) + str(randint(0,2048)) 


class FileRecorder( DataConsumer ):
    """
    FileRecorder is an output component for received and processed data streams.
    It is a DataConsumer and muste therefor be started with start() to be active.
    It records data of 
    """
    
    def __init__( self, blackboard, patterns, channels, types, writer ):
        """
        @param blackboard:
            The blackboard containing the databuffers of the patterns that are to be recorded
        @param patterns:
            The patterns pointing to the data buffers on the blackboard that will be recorded
        @param channels
            The channel numbers corresponding to the specified patterns
        @param _types:
            The data _types corresponding to the specified patterns
            
        The length of patterns, channels and _types are all paired and their length should therefore be equal
        """
        if len(channels) != len(patterns) or len(types) != len(patterns):
            raise ValueError('Number of patterns, channels and _types should be equal')
        
        DataConsumer.__init__(self,blackboard,patterns)
        
        self._blackboard        = blackboard
        self._channels          = channels
        self._types             = types
        self._writer            = writer
        self._global_rec_start  = 0
        self._last_timestamp    = 0
        self._first             = []
        self._rec_start         = []
        
        self.reset()
        
        self._recording = False
        self._filename = random_filenames()


    def reset(self):
        """ 
        reset all internal buffers 
        """
        self._samples                   = {}
        for pattern in self._patterns:
            self._samples[pattern]      = []
            self._blackboard.clear(pattern)

        self._first = [ True for _ in range( len(self._patterns) )]
        self._rec_start = [ 0.0 for _ in range( len(self._patterns) )]


    def start_recording(self, start_time):
        """
        Start datarecording for the specified data patterns
        Start time will be stored as reference for frequency calculation
        """
        # TODO: check whether all variables are set correctly
        if not self._recording:
            self.reset()
            # print 'Recording started at:', start_time
            self._global_rec_start = start_time

#             self._rec_start = CoreTime().now()
#             self._rec_start = self._last_timestamp

            self._recording = True
    
    
    def stop_recording(self):
        """ 
        Stop recording and write data to file with specified filename (appended with file extension) 
        """
        if self._recording:
            # total recording time for frequency estimation
#             total_time = CoreTime().now() - self._rec_start
            
            total_time = self._last_timestamp - self._global_rec_start
        
            self._recording = False
            
            data_recorded = False      
            for p in self._patterns:
                data = self._samples.get( p, [] )
                if len( data ) > 0:
                    data_recorded = True
                    break;
            
            if not data_recorded:
                return
            
            self._writer.createEEGFile( self._filename )

            # Write samples
            for pattern, (channel, data_type) in zip(self._patterns,zip(self._channels, self._types )):
                data            = self._samples.get( pattern )
                data_length     = len( data )
                freq            = round( data_length / total_time )
                if len( data ) > 0:
                    self._writer.write(data_type, channel, freq, data)

            # Write marker-data if set
            blackboard_markers = self._blackboard.get_data(PatternStrings.MARKERS)
            marker_data = blackboard_markers['data']
            marker_time = blackboard_markers['timestamps']
            
            if marker_data != [] and marker_time != []:
                m_time = []
                for t in marker_time:
                    m_time.append(t - self._global_rec_start)
                    
                markers = zip(marker_data, m_time)
                self._writer.write_markers(markers)
            
            self._writer.closefile()
            self.reset()
    
    
    def _process_data(self, pattern, data, timestamps ):
        """
        Inherited from DataConsumer
        Stores received data in local data buffer
        """
        if self._recording:
            for index, pat in enumerate(self._patterns):
                if pat is pattern:
                    break
            self._last_timestamp = max(timestamps)
            if self._first[index] is True:
                #print pattern, min(timestamps), max(timestamps)
                self._rec_start[index] = self._last_timestamp
                print 'Start recording for %s from timestamp: %f' % (pattern, self._last_timestamp)
                self._first[index] = False
                # First recorded sample is latest data from buffer and starts always at 0.0 s
                self._samples[pattern].append([data[-1], 0.0])
            else:
                for d, t in zip(data, timestamps):
                    if t >= self._rec_start[index]:
                        self._samples[pattern].append( [d, t - self._rec_start[index]] )
                    else:
                        print 'Rec timing error for %s (%f, %f)' % (pattern, self._rec_start[index], t)
                    
    
    def set_filename(self, filename):
        """ 
        Sets the filename for the data file 
        """
        self._filename = filename
    
    def get_filename(self):
        return self._filename
    
    def is_recording(self):
        """ 
        boolean whether the object is currently recording 
        """
        return self._recording
    
    
    def get_duration(self):
        return self._last_timestamp - self._global_rec_start
