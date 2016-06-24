# -*- coding: utf-8 -*-
"""
This python program opens a predefined HDF file  
then filters the data and visualizes the data EEG.

The HDF file contains six types of data for eight channels.
The EEG stream for the first channel is visualised.

Used libraries are:

mne         -> for filtering and other EEG analytics

numpy       -> for mathmetics

MatplotLib  -> for plotting

h5py        -> for reading HDF files

"""

import mne
import numpy as np
import matplotlib.pyplot as plt
import sys

from root.input.hdfreader import HDFReader
from root.data import filenames

def plotLotsOfData():   
    """
    This function is basically a script for trying out a number of functionalities.
    
    1: First, a file is read using the HDFFilreader.
    
    2: From that file, two EEG channels are isolated.
    
    3: Different band-pass filters are applied using MNE's Filter package
    
    4: Activation of a filter band in a time-window is calculated (!!! But this is done in the wrong way! Do not use this!!!)
    
    5: The left and right channels filtered information is combined into valence and arousel values 
    
    6: All these steps are repeated for the paired data file
    
    7: All this information is plotted
    """
     
     
    def smooth(data, windowSize=25):
        """
        """
        return [ sum(abs( data[i:i+windowSize]) ) / windowSize for i in range(len(data)) ]
    
    # Default filename 
    filename = filenames[0][0]
    filename2 = filenames[0][1]
    # If argument is given, change filename
    if len( sys.argv ) > 1:
        filename = sys.argv[1];
    
    # Initialize data reader
    reader = HDFReader();
    
    # 1: Read data
    [ mat, frequencies] = reader.read( filename )
    
    # 2: Take data from channel 0, type 1 (EEG)
    destL = np.asarray( mat[0][1] )[:];
    
    # Take data from channel 2, type 1 (EEG)
    destR = np.asarray( mat[2][1] )[:];
    
    # Frequency of eeg data 
    eegFrequency = frequencies[1];
    
    # 3: Apply different band-pass filters
    alphaL = mne.filter.band_pass_filter( destL, eegFrequency, 8, 14 ); # center = 12
    betaL = mne.filter.band_pass_filter( destL, eegFrequency, 17, 31 ); # center = 24
     
    alphaR = mne.filter.band_pass_filter( destR, eegFrequency, 8, 14 ); # center = 12
    betaR = mne.filter.band_pass_filter( destR, eegFrequency, 17, 31 ); # center = 24
     
    print ('Done filters 1') 
     
    windowSize = 100;
     
    # 4: filtered activations
    alphaActL = np.log( [ sum(abs( alphaL[i:i+windowSize]) ) / (windowSize / 12.0) for i in range(len(alphaL)) ] )
    betaActL = np.log( [ sum(abs( betaL[i:i+windowSize]) ) / (windowSize / 24.0) for i in range(len(betaL)) ] )
     
    alphaActR = np.log( [ sum(abs( alphaR[i:i+windowSize]) ) / (windowSize / 12.0) for i in range(len(alphaR)) ] )
    betaActR = np.log( [ sum(abs( betaR[i:i+windowSize]) ) / (windowSize / 24.0) for i in range(len(betaR)) ] )
     
    print ('Done activations 1') 
     
    # 5: Combined values
    arousal = ( betaActL+betaActR ) / ( alphaActL + alphaActR );
    valence = ( alphaActL / betaActL ) - ( alphaActR / betaActR );
     
    arousal = smooth( arousal , 1000 );
    valence = smooth( valence , 1000 );
     
    print ('Done combination 1') 
     
    plotOffset = 0;
    plotLength = 256 * 100;
     
    plt.close();
    f, ax = plt.subplots(4,5);
     
    ax[0,0].plot( alphaL.tolist()[plotOffset:plotOffset+plotLength] )
    ax[1,0].plot( betaL.tolist()[plotOffset:plotOffset+plotLength] )
     
    ax[0,1].plot( alphaActL[plotOffset:plotOffset+plotLength] )
    ax[1,1].plot( betaActL[plotOffset:plotOffset+plotLength] )
      
    ax[0,4].plot( alphaR.tolist()[plotOffset:plotOffset+plotLength] )
    ax[1,4].plot( betaR.tolist()[plotOffset:plotOffset+plotLength] )
      
    ax[0,3].plot( alphaActR[plotOffset:plotOffset+plotLength] )
    ax[1,3].plot( betaActR[plotOffset:plotOffset+plotLength] )
      
    # center
    ax[0,2].plot( arousal[plotOffset:plotOffset+plotLength] );
    ax[1,2].plot( valence[plotOffset:plotOffset+plotLength] );
           
    print ('Done plots 1') 
    
          
    ######################################################################
     
    # 6: 
     
    # Read data 
    [ mat2, frequencies] = reader.read( filename2 )
    
    # Take data from channel 0, type 1 (EEG)
    dest2L = np.asarray( mat2[0][1] )[:];
    
    # Take data from channel 2, type 1 (EEG)
    dest2R = np.asarray( mat2[2][1] )[:];
       
    alpha2L = mne.filter.band_pass_filter( dest2L, eegFrequency, 8, 14 ); 
    beta2L = mne.filter.band_pass_filter( dest2L, eegFrequency, 17, 31 ); 
     
    alpha2R = mne.filter.band_pass_filter( dest2R, eegFrequency, 8, 14 ); 
    beta2R = mne.filter.band_pass_filter( dest2R, eegFrequency, 17, 31 ); 
      
    print ('Done filters 2') 
    
    alphaAct2L = np.log( [ sum(abs( alpha2L[i:i+windowSize]) ) / (windowSize / 12.0) for i in range(len(alpha2L)) ] )
    betaAct2L = np.log( [ sum(abs( beta2L[i:i+windowSize]) ) / (windowSize / 24.0) for i in range(len(beta2L)) ] )
     
    alphaAct2R = np.log( [ sum(abs( alpha2R[i:i+windowSize]) ) / (windowSize / 12.0) for i in range(len(alpha2R)) ] )
    betaAct2R = np.log( [ sum(abs( beta2R[i:i+windowSize]) ) / (windowSize / 24.0) for i in range(len(beta2R)) ] )
      
    print ('Done activations 2') 
    
    # Combined
    arousal2 = ( betaAct2L+betaAct2R ) / ( alphaAct2L + alphaAct2R );
    valence2 = ( alphaAct2L / betaAct2L ) - ( alphaAct2R / betaAct2R );
     
    arousal2 = smooth( arousal2 , 1000 );
    valence2 = smooth( valence2 , 1000 );
     
    print ('Done combinations 2') 
     
    # 7 plotting
    
    ax[2,0].plot( alpha2L.tolist()[plotOffset:plotOffset+plotLength] )
    ax[3,0].plot( beta2L.tolist()[plotOffset:plotOffset+plotLength] )
     
    ax[2,1].plot( alphaAct2L[plotOffset:plotOffset+plotLength] )
    ax[3,1].plot( betaAct2L[plotOffset:plotOffset+plotLength] )
      
    ax[2,4].plot( alpha2R.tolist()[plotOffset:plotOffset+plotLength] )
    ax[3,4].plot( beta2R.tolist()[plotOffset:plotOffset+plotLength] )
      
    ax[2,3].plot( alphaAct2R[plotOffset:plotOffset+plotLength] )
    ax[3,3].plot( betaAct2R[plotOffset:plotOffset+plotLength] )
      
    # center
    ax[2,2].plot( arousal2[plotOffset:plotOffset+plotLength] );
    ax[3,2].plot( valence2[plotOffset:plotOffset+plotLength] );
             
    print ('Done plots 2') 
    
    plt.show();
    
if __name__ == '__main__':
    plotLotsOfData()