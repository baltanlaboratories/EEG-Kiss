'''
Created on Oct 19, 2015

@author: Sjors.Ruijgrok
'''
import logging
import serial


class SerialSocket(object):
    '''
    classdocs
    '''

    def __init__(self, port = None):
        '''
        Constructor
        '''
        self.logger = logging.getLogger()
        
        if port != None:
            self._socket = serial.Serial(port = port, timeout = 5, writeTimeout = 1)
            self.logger.log(logging.INFO, (__file__, ": Opened a serial connection on port: ", self._socket._port))
        else:
            self._socket = None

    def send(self, data = None):
        if self._socket != None:
            self._socket.write(data)

    def recv(self, size):
        if self._socket != None and size > 0:
            return self._socket.read(size)
        return 0

    def close(self):
        if self._socket != None:
            self._socket.close()
            self.logger.log(logging.INFO, (__file__, ": Closed serial connection on port: ", self._socket._port))

    def port(self):
        if self._socket != None:
            return self._socket._port
        return ''
