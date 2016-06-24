from random import randint
import OSC
import time
import threading

client = OSC.OSCClient()
client.connect(('127.0.0.1', 7110))   # connect to SuperCollider


samplerate = 265.
samplerate = 32.

def simulate():
    print 'Simulation stared on localhost port 7110'
    strt = time.clock()
    indx = 0

    while True:
        new_indx = int((time.clock() - strt) * samplerate)
        if new_indx > indx:
            for i in range(2):
                for c in range(1,5):
                    oscmsg = OSC.OSCMessage()
                    oscmsg.setAddress("/eeg%d/channel_%d"%(i,c))
                    oscmsg.append( randint(0,4096)/4096. )
                    client.send(oscmsg)
            indx += 1
            
t = threading.Thread(target=simulate)
t.daemon = True
t.start()

raw_input('\nPress enter to exit...')