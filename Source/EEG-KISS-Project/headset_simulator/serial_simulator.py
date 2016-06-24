import argparse
import logging
import numpy                    as np
import os
import simConstants
import serial
import serial.tools.list_ports
import struct
import sys
import threading
import time

from time                       import clock
from random                     import random, randint
from math                       import sin
from functools                  import partial
from root.core.processingthread import ProcessingThread

path = os.path.dirname(os.path.abspath(__file__))+'\..\..'
sys.path.append(path)

###################################################################################################
class DataGenerator( ProcessingThread ):
    
    def __init__( self, frequencies=[], amplitudes=[], noise=0, offset=0, Fs=256 ):
        
        if len(frequencies) != len(amplitudes):
            raise TypeError( 'number of frequencies and amplitudes should be equal' )
        
        ProcessingThread.__init__( self )
        
        self._frequencies       = frequencies
        self._amplitudes        = amplitudes
        self._noise             = noise
        self._offset            = offset
        self._Fs                = Fs
        
        self._start_time        = clock()
        self._processed_samples = 0

    def get_samples(self):
        """
        Inherited from ProcessingThread
        """
        now                 = clock()
        dif                 = now - self._start_time
        tmp                 = dif * self._Fs
        tmp_round           = round(tmp)
        total_nr_samples    = int(tmp_round)
        
        #print tmp, tmp_round, total_nr_samples
        
        samples = []
        
        for i in range( self._processed_samples, total_nr_samples ):
            y       = 0
            for freq, amp in zip(self._frequencies, self._amplitudes):
                y += amp * np.sin( 2*np.pi*freq*i / self._Fs )  
            n       = 2*self._noise*random() - self._noise
            value   = y + n + self._offset
            samples.append(int(value))
        self._processed_samples = total_nr_samples
        
        return samples

    def start(self):
        """
        Overrides ProcessingThread
        """
        if not self._running:
            self._start_time = clock()
        ProcessingThread.start( self )


###################################################################################################
class SerialPort:
    def __init__(self, port = 'COM3'):
        self._port  = port
        self.logger = logging.getLogger()
        
        #ports = list(serial.tools.list_ports.comports())
        #print ports
        #used_ports = [c[0] for c in ports]

        # ser = serial.Serial(port, timeout=1, writeTimeout=1, baudrate = 115200)  # open serial port
        self._ser = serial.Serial(port, writeTimeout = 1)  # open serial port
        self.logger.log(logging.CRITICAL, (__file__, ": Opened port - ", self._ser._port))       
        
        self._ser.setBaudrate(115200)
        self.logger.log(logging.CRITICAL, (__file__, ": Set baudrate - ", self._ser.getBaudrate()))   

    def close(self):
        self._ser.close() 
    
    def write(self, data_packet):
        self._ser.write(data_packet)

    def flush(self):
        self._ser.flush()

    def isOpen(self):
        return self._ser.isOpen()


###################################################################################################
class SerialSimulator:
    def __init__(self, port = None, random = False, signal = None):
        self.logger   = logging.getLogger()

        self._sp = SerialPort(port)
        self._random  = random

        if signal != None:
            self._signal = signal
        else:
            # Set default freq and ampl
            chan_freq = simConstants.DEFAULT_FREQ
            chan_ampl = simConstants.DEFAULT_AMPL
            self._signal = []

            for i in range(4):
                self._signal.append(DataGenerator([(chan_freq[i])], [chan_ampl[i]], offset = simConstants.PARAM_AMPL_MAX))

    def start(self):
        self._hs_simulator = threading.Thread(target = partial(self._loop, self._random, self._signal))
        self._hs_simulator.daemon = True
        self._hs_simulator.start()

    def stop(self):
        self._sp.close()
        self.logger.log(logging.CRITICAL, (__file__, ": Closed port - ", self._sp._port))       
    
    def _loop(self, bRandomize, signal):
        self.logger.log(logging.CRITICAL, (__file__, ": Serial simulator loop started"))

        sample_buffer = []

        for i in range(len(signal)):
            sample_buffer.append([])    # add inner list for each channel

        packets_count = -1
        while True:
            if self._sp.isOpen():

                # generate samples for all channels
                for i in range(len(signal)):
                    new_samples = signal[i].get_samples()
                    sample_buffer[i] = sample_buffer[i] + new_samples

                # make data-packet when we have minimal 16 samples per channel
                if len(sample_buffer[0]) > 15:
                    packets_count += 1

                    # add samples from each channel of sample_buffer to new list
                    samples = []    # create list

                    for i in range(len(signal)):
                        samples.append(sample_buffer[i][:16])       # read oldest 16 samples from sample_buffer
                        sample_buffer[i] = sample_buffer[i][16:]    # remove oldest 16 samples from sample_buffer
                        # print '{} channel {}: {}'.format(packets_count, i, samples[i])

                    data_packet = self._make_data_packet(samples, packets_count)

                    # Check real-time behavior
                    # t = (clock() - start_time)
                    # c = packets_count / 16
                    # print t, c, round(t - c)

                    try:
                        self._sp.write(data_packet)
                    except Exception as e:
                        self.logger.log(logging.CRITICAL, (__file__, ":Exception serial-simulator -> ", e))

                    if bRandomize:
                        # Randomize each 4 s (1 packet = 16 samples, fs = 256 Hz -> 16/256 = 0.0625 s/packet -> 64*0.0625 = 4 s
                        if packets_count % 64 == 0:
                            randomize(signal)

                time.sleep(0.0625)

    def _make_eeg_packet(self, sample):
        packet = []

        for i in range(8):
            packet += [ ord(c) for c in struct.pack('<H', sample[i]) ]

        return packet

    def _make_data_packet(self, samples, sample_number):
        '''
        @param samples              2D array: [4 channels][16 samples]
        @param sample_number        incremented number used for time-stamp generation
        '''
        if len(samples) > 8:
            raise TypeError('number of sample-channels is greater than actual number of channels in a packet')
        if len(samples[0]) != 16:
            raise TypeError('number of samples per channel has an unexpected value')

        # Make sample-blocks
        sample_block = []
        packets      = []

        for block_index in range(4):
            # add inner list
            sample_block.append([])

            for eeg_index in range(4):
                # add inner list of 8 zero's
                sample_block[block_index].append([0] * 8)

                # fill inner list with samples, take a sample from each channel
                for chan in range(4):
                    sample_block[block_index][eeg_index][chan] = samples[chan][block_index * 4 + eeg_index]

            packets += self._make_eeg_packet(sample_block[block_index][0])
            packets += self._make_eeg_packet([0] * 8)    # IMP sample
            packets += self._make_eeg_packet(sample_block[block_index][1])
            packets += self._make_eeg_packet(sample_block[block_index][2])
            packets += self._make_eeg_packet(sample_block[block_index][3])

        preamble    = [ord(c) for c in 'BAN']
        command     = [ord('d')]
        timestamp   = [ ord(c) for c in struct.pack('<I', sample_number * 4096) ] # get timestamp in there
        id          = [0]
    
        payload = []
        payload += command
        payload += timestamp
        payload += id
        payload += packets

        length = [ord(c) for c in struct.pack('<H', len(payload)) ]

        packet = []

        packet += preamble
        packet += length
        packet += payload
        
        return packet


###################################################################################################
def randomize(signal):
    for chan in range(len(signal)):
        signal[chan]._frequencies = [randint(1,66) for _ in range(3)]
        signal[chan]._amplitudes  = [randint(100,666) for _ in range(3)]
        # NOTE: With offset=2000, max. amplitude with 3 signals is 2000/3, else we can get negative sample-values.

        # If needed for debug info log this. For now not needed since this is only terminal polution
        #print signal[chan]._frequencies, signal[chan]._amplitudes


###################################################################################################
def freqIsValid(freq):
    return freq >= simConstants.PARAM_FREQ_MIN and freq <= simConstants.PARAM_FREQ_MAX


###################################################################################################
def amplIsValid(amplitude):
    return amplitude >= simConstants.PARAM_AMPL_MIN and amplitude <= simConstants.PARAM_AMPL_MAX


###################################################################################################
def processArguments():
    parser = argparse.ArgumentParser(
        description='Simulate an Imec headset with four channels',
        epilog="Note the max frequency is 60 and the max amplitude is 2000"
    )

    parser.add_argument(
        "-ch1",
        "--channel1",
        nargs=2,
        action="store",
        type=int,
        help="Channel 1 frequency and amplitude"
    )

    parser.add_argument(
        "-ch2",
        "--channel2",
        nargs=2,
        action="store",
        type=int,
        help="Channel 2 frequency and amplitude"
    )

    parser.add_argument(
        "-ch3",
        "--channel3",
        nargs=2,
        action="store",
        type=int,
        help="Channel 3 frequency and amplitude"
    )

    parser.add_argument(
        "-ch4",
        "--channel4",
        nargs=2,
        action="store",
        type=int,
        help="Channel 4 frequency and amplitude"
    )

    parser.add_argument(
        "-r",
        "--random",
        action="store_true",
        default=False,
        help="Randomize frequencies using base frequencies of all channels"
    )

    parser.add_argument(
        '-p',
        '--port',
        action = 'store',
        help = 'Select comport for streaming simulated headset data'
    )

    args = parser.parse_args()

    logger = logging.getLogger()
    logger.log(logging.CRITICAL, (__file__, ": The following arguments are processed - ", args))

    if args.channel1 != None:
        if freqIsValid(args.channel1[0]) and amplIsValid(args.channel1[1]):
            chan_freq[0] = args.channel1[0]
            chan_ampl[0] = args.channel1[1]
        else:
            sys.exit("Channel 1 args invalid. Check simConstants.py")
    if args.channel2 != None:
        if freqIsValid(args.channel2[0]) and amplIsValid(args.channel2[1]):
            chan_freq[1] = args.channel2[0]
            chan_ampl[1] = args.channel2[1]
        else:
            sys.exit("Channel 2 args invalid. Check simConstants.py")
    if args.channel3 != None:
        if freqIsValid(args.channel3[0]) and amplIsValid(args.channel3[1]):
            chan_freq[2] = args.channel3[0]
            chan_ampl[2] = args.channel3[1]
        else:
            sys.exit("Channel 3 args invalid. Check simConstants.py")
    if args.channel4 != None:
        if freqIsValid(args.channel4[0]) and amplIsValid(args.channel4[1]):
            chan_freq[3] = args.channel4[0]
            chan_ampl[3] = args.channel4[1]
        else:
            sys.exit("Channel 4 args invalid. Check simConstants.py")
    return args


###################################################################################################
if __name__ == '__main__':

    logger = logging.getLogger()

    # Set default freq and ampl
    chan_freq = simConstants.DEFAULT_FREQ
    chan_ampl = simConstants.DEFAULT_AMPL

    args = processArguments()

    signal = []
    for i in range(4):
        signal.append(DataGenerator([(chan_freq[i])], [chan_ampl[i]], offset = simConstants.PARAM_AMPL_MAX))

    hs_simulator = SerialSimulator(args.port, args.random, signal)
    hs_simulator.start()

#     sp = SerialPort()
    logger.log(logging.CRITICAL, (__file__, ": Serial simulator started - ", args))
    print 'Serial simulator started. Press enter to leave...'


#     printer = threading.Thread(target = partial(loop, args.random, signal))
#     printer.daemon = True
#     printer.start()

    # Wait for user to stop the simulator
    raw_input()
    
#     sp.close()
    hs_simulator.stop()
