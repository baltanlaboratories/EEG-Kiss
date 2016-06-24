# -*- coding: utf-8 -*-
"""
The HDF reader is used to read the HDF5 files that were provided by Baltan Laboratories and that are included in the 'data' package.

The file is parsed using the h5py library.
"""

import h5py
import numpy as np
from abstractfilereader import AbstractFilereader

class HDFReader ( AbstractFilereader ):

    def read( self, filename ):        
        """
        @param filename:        
            Will read the file corresponding to the given filename.     
            This file is assumed to be an HDF5 file of the correct format.
        @return mat:
            matrix with data for all channels for six types of data  
        @return frequencies:
            vector of frequency values for each data type
        """

        # Assume file is an Imec file
        if not h5py.is_hdf5( filename ):
            raise TypeError("File is not a HDF5 file")
            
        f = h5py.File(filename, "r")
        
        """ Initiate data matrix
            3-dimensional list for:
                8 channels of the eeg headset
                6 types of data
                unknown number of samples
        """
        mat = [[[] for _ in range(6)] for _ in range(8)];
        markers = None
        
        types = ['DC','EEG','EEGA','ImpI','ImpIQ','ImpQ']
        
        """ Read data packages """      
        signal = f.get('/Signal')
        for i in range(1,9):
            for index, type in enumerate(types):
                mat[i-1][index] = np.float64( signal.get( type + '-' + str( i ) ).get('data') )
        
        """ Read frequency values """
        frequencies = [0 for _ in range(6)];
        for index, type in enumerate(types):
            frequencies[index] = np.float64( signal.get( type + '-1' ).attrs.get('freq') )
        
        """ Read markers """
        item_markers = signal.get('Markers')
        if item_markers != None:
            item_markers_data = item_markers.get('data')
            if item_markers_data != None:
                markers = np.float64(item_markers_data)
        
        return [ mat, frequencies, markers ];
