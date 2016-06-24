import serial
import sys
import threading

import serial.tools.list_ports

if __name__ == '__main__':
    print 'Serial monitor started'
    ports = list(serial.tools.list_ports.comports())
    print ports
    used_ports = [c[0] for c in ports]
    
    port = 'COM14'
    print 'Monitoring port: %s' % port
    print 'Press enter to leave...'
    ser = serial.Serial(port)  # open first serial port
	
    def loop():
        while True:
            data = ser.read(8)
            for byte in data:
                try:
                    print ord(byte.encode('utf-8'))
                except:
                    pass
    printer = threading.Thread(target=loop)
    printer.daemon = True
    printer.start()
    
    raw_input()
	
    ser.close() 