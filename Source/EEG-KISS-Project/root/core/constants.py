'''
Created on 7 mei 2015

@author: Bas.Kooiker
'''

class Markers:
    KISS_STOP       = 0
    KISS_START      = 1
    POI             = 2     # Point of interest
    REC_START       = 3
    REC_STOP        = 4
    
    Color = [ 'c', 'g', 'r', 'm', 'b' ]  # cyan, green, red, magenta, blue

class States:
    IDLE            = 0
    BUSY            = 1
    
class BufferTypes:
    ORIGINAL        = 'Blackboard buffer'
    CIRCULAR        = 'Circular buffer'
    ORDINARY        = 'Ordinary buffer'

class PatternStrings:
    SIGNAL_EEG      = '/EEG_'
    SIGNAL_IMPI     = '/ImpI'
    SIGNAL_IMPQ     = '/ImpQ'
    CHANNEL         = '/channel_'
    FILTERNOTCH     = '/notch_50'
    FILTERLPF       = '/lpf_75'
    MARKERS         = '/markers'
    FFT             = '/fft'
    DELTA           = '/delta'
    THETA           = '/theta'
    ALPHA           = '/alpha'
    BETA            = '/beta'
    GAMMA           = '/gamma'
    AROUSAL         = '/arousal'
    VALENCE         = '/valence'

class SignalNames:
    RAWSIGNAL       = 'EEGA'
    FILTEREDSIGNAL  = 'EEG'

class FilterSettings:
    NOTCH_NUMTAPS   = 129   # Number of coefficients for notch filter
    NOTCH_FS        = 256   # Sample frequency for notch filter (Hz)
    NOTCH_FREQ      = 50    # Suppressed frequency for notch filter (Hz)
    LPF_NUMTAPS     = 33    # Number of coefficients for low-pass filter
    LPF_FS          = 256   # Sample frequency for low-pass filter (Hz)
    LPF_FREQ        = 75    # Cut-off frequency for low-pass filter

class VisualisationTypes:
    TIME = 'Signal - Time'
    FREQUENCY = 'Intensity - Frequency'
    FREQUENCY_BAND = 'Frequency band - Time'
    AROUSEL = 'Arousel - Time'
    VALENCE = 'Valence - Time'

class ChannelTypes:
    LEFT= 'Left channel'
    MID= 'Middle channel'
    RIGHT= 'Right channel'
    BACK= 'Back channel'
    
    values = {}
    names = {}
    
    values[RIGHT] = 1
    names[1]=RIGHT
    
    values[MID] = 2
    names[2]=MID
    
    values[LEFT] = 3
    names[3]=LEFT
    
    values[BACK] = 4
    names[4]=BACK

class FrequencyBands:
    DELTA = 'Delta (0.5-4 Hz)'
    THETA = 'Theta (4-8 Hz)'
    ALPHA = 'Alpha (8-14 Hz)'
    BETA = 'Beta (14-31 Hz)'
    GAMMA = 'Gamma (31-48 Hz)'
    
    values = [DELTA, THETA, ALPHA, BETA, GAMMA]
    
    patterns = {}
    patterns[DELTA] = PatternStrings.DELTA
    patterns[THETA] = PatternStrings.THETA
    patterns[ALPHA] = PatternStrings.ALPHA
    patterns[BETA] = PatternStrings.BETA
    patterns[GAMMA] = PatternStrings.GAMMA

class Testing:
    SERIAL_SIMULATOR = False  # Set True when testing with serial_simulator
    SERIAL_PORT = 'COM15'     # Set COM-port used by com0com-tool (connects COM-port of serial_simulator to other local COM-port)
