'''
Created on Jul 3, 2015

@author: Sjors.Ruijgrok
'''
import logging
import numpy
import threading
from _collections import defaultdict

class CircularBuffer(object):
    
    DEFAULT_BUFSIZE = 512
    
    def __init__(self, pattern, size = DEFAULT_BUFSIZE):
        """initialization"""
        self._pattern    = pattern
        self._size       = size
        self._data       = []
        self._timestamps = [] 
        self._index      = 0
        self._count      = 0
        self._lock       = threading.Lock()
        self.logger      = logging.getLogger()
    
    def put_data(self, value, timestamp = None):
        """ Append an element """
        if not isinstance( value, numpy.ndarray ):
            if not isinstance(value, list):
                value = [value]
        
        with self._lock:
            for v in value:
                if len(self._data) == self._size:
                    self._data[self._index] = v
                    self._timestamps[self._index] = timestamp
                else:
                    self._data.append(v)
                    self._timestamps.append(timestamp)
            
            self._count += len(value)
            self._index = (self._index + len(value)) % self._size
    
    def get_data(self, count = None):
        """ Retrieve count elements or all elements if no count provided """
        
        #=!=!=!=!=!=!=!=!=!=!=!=!=!=! NOTE !=!=!=!=!=!=!=!=!=!=!=!=!=!=
        # If performance is an issue, declare the dict once in __init__ 
        # to prevent rebuilding the dictionary every call
        
        if count == None:
            count = self._size
        elif count == 0:
            return defaultdict(list, data=[], timestamps=[])
        
        with self._lock:
            data = self.get_data_values(count)
            timestamps = self.get_timestamp_values(count)
            
        return defaultdict(list, data=data, timestamps=timestamps)       

    def get_data_values(self, count = None):
        """ Returns the data from this buffer """
        if len(self._data) == self._size:
            if count >= self._size:
                # Return all
                data = self._data[self._index : ] + self._data[ : self._index]
            else:
                # Return part
                if count <= self._index:
                    data = self._data[self._index - count : self._index]
                else:
                    data = self._data[self._index - count : ] + self._data[ : self._index]
        else:
            if count > self._index:
                count = self._index
            data = self._data[self._index - count : ]
        
        return data
    
    def get_data_window(self, first, last):
        if not len(self._data) > 0:
            return []
        try:
            if not first == None:
                index_first = self._timestamps.index(first)
            else:
                index_first = 0
        
            index_last = self._timestamps.index(last)
            
            if index_first > index_last:
                firstPart = self._data[index_first:]
                lastPart  = self._data[:index_last]

                return firstPart + lastPart
            else:
                return self._data[index_first:index_last]
        except Exception as e:
            #print last, " could not be found"
            return []
            
    
    def get_timestamp_values(self, count = None):
        """ Returns the timestamps from this buffer """
        if len(self._timestamps) == self._size:
            if count >= self._size:
                # Return all
                timestamps = self._timestamps[self._index : ] + self._timestamps[ : self._index]
            else:
                # Return part
                if count <= self._index:
                    timestamps = self._timestamps[self._index - count : self._index]
                else:
                    timestamps = self._timestamps[self._index - count : ] + self._timestamps[ : self._index]

            if count != len(timestamps):
                self.logger.log(logging.CRITICAL, (__file__, ": get_timestamp_values() - mismatch: count=" ,count, " length=" ,len(timestamps), " index=" ,self._index))
        else:
            if count > self._index:
                count = self._index

            timestamps = self._timestamps[self._index - count : ]
        
        return timestamps
    
    def get_timestamps_window(self, first, last):
        if not len(self._timestamps) > 0:
            return []
        
        if not first == None:
            index_first = self._timestamps.index(first)
        else:
            index_first = 0
            
        index_last = self._timestamps.index(last)
        
        if index_first > index_last:
            firstPart = self._timestamps[index_first:]
            lastPart  = self._timestamps[:index_last]

            return firstPart + lastPart
        else:
            return self._timestamps[index_first:index_last]
            
    
    def clear(self):
        """ remove all collected data """
        with self._lock:
            self._data       = []
            self._timestamps = [] 
            self._index      = 0
            self._count      = 0
    
    ### SETTERS ###
    def set_bufsize(self, size):
        """
        @param bufferlength 
            Sets the specified buffer length
        """
        self._size = size
    
    ### GETTERS ###
    def get_bufsize(self):
        """ Returns the current buffer length """
        return self._size
    
    def get_count(self):
        """ Returns the sample counter of this data buffer"""
        return self._count
    
    def get_pattern(self):
        """ returns the pattern of this data buffer """
        return self._pattern
    
    def get_all(self):
        """return a list of all the elements"""
        return self._data
    
    def __getitem__(self, key):
        """get element by index like a regular array"""
        return self._data[key]
    
    def __repr__(self):
        """return string representation"""
        return self._data.__ge__repr__() + ' (' + str(len(self._data))+' items)'
    
    def get_last_timestamp(self):
        """ return the last timestamp of this data buffer """
        if len(self._timestamps) > 0:
            tmp = self._timestamps[self._index-1]
            return tmp
        else:
            return 0