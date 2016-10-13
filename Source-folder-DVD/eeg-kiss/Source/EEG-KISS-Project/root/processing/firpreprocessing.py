from scipy.signal           import lfilter

from root.core.dataconsumer import DataConsumer

class FIRPreprocessing ( DataConsumer ):
    """
    This class does serial filtering with first a 50Hz notch filter, then a low-pass filters.
    The results are stored back on the blackboard with the same pattern appended with /pp (Pre-processing)
    The FIR coefficients are fixed for 256 Hz sample rate and the predefined cutoff frequencies.
    """
    
    coefLPF256 = [1.1232059e-003,  1.1208378e-003, -2.3017715e-003, -1.2968676e-003,  5.5755995e-003,  4.0308284e-004, -1.1507168e-002,  3.8618428e-003,  
                  1.9811780e-002, -1.4693275e-002, -2.9307068e-002,  3.7453994e-002,  3.8179880e-002, -8.8308294e-002, -4.4495784e-002,  3.1147448e-001,  
                  5.4581104e-001,  3.1147448e-001, -4.4495784e-002, -8.8308294e-002,  3.8179880e-002,  3.7453994e-002, -2.9307068e-002, -1.4693275e-002,  
                  1.9811780e-002,  3.8618428e-003, -1.1507168e-002,  4.0308284e-004,  5.5755995e-003, -1.2968676e-003, -2.3017715e-003,  1.1208378e-003,  
                  .1232059e-003]
    
    coefBSF256 = [7.9515685e-004 ,  2.7195643e-004 , -6.3251873e-004 , -7.0917230e-004 ,  1.6205395e-004 ,  8.1777468e-004 ,  3.8234364e-004 , -5.2325836e-004 , 
                  -6.7060244e-004 ,  3.1681939e-005 ,  5.1009407e-004 ,  2.2784377e-004 , -1.0493663e-004 ,  5.0633916e-005 ,  3.3743632e-005 , -6.2339213e-004 , 
                  -7.7005318e-004 ,  6.5911624e-004 ,  2.0346089e-003 ,  6.2995158e-004 , -2.6430721e-003 , -3.0469159e-003 ,  1.2843847e-003 ,  5.0518255e-003 ,  
                  2.1724849e-003 , -4.6407132e-003 , -5.9936730e-003 ,  1.0643788e-003 ,  7.4672547e-003 ,  4.0362308e-003 , -5.0384904e-003 , -7.4035031e-003 , 
                  -2.2464560e-017 ,  6.6871000e-003 ,  4.0462353e-003 , -2.7762071e-003 , -4.0732884e-003 , -3.8520650e-004 ,  7.1310304e-004 , -9.6388816e-004 ,  
                  1.4169052e-003 ,  6.3834709e-003 ,  2.7160754e-003 , -1.0107353e-002 , -1.3347255e-002 ,  4.7960396e-003 ,  2.3498038e-002 ,  1.1817182e-002 , 
                  -2.2473689e-002 , -3.2545186e-002 ,  3.9454568e-003 ,  4.3156412e-002 ,  2.7037050e-002 , -3.1412275e-002 , -5.4201866e-002 , -2.9610057e-003 ,  
                  5.8943362e-002 ,  4.4968317e-002 , -3.2898315e-002 , -7.1465387e-002 , -1.4496041e-002 ,  6.5129781e-002 ,  5.9608195e-002 , -2.6218589e-002 ,  
                  9.2115922e-001 , -2.6218589e-002 ,  5.9608195e-002 ,  6.5129781e-002 , -1.4496041e-002 , -7.1465387e-002 , -3.2898315e-002 ,  4.4968317e-002 ,  
                  5.8943362e-002 , -2.9610057e-003 , -5.4201866e-002 , -3.1412275e-002 ,  2.7037050e-002 ,  4.3156412e-002 ,  3.9454568e-003 , -3.2545186e-002 , 
                  -2.2473689e-002 ,  1.1817182e-002 ,  2.3498038e-002 ,  4.7960396e-003 , -1.3347255e-002 , -1.0107353e-002 ,  2.7160754e-003 ,  6.3834709e-003 ,  
                  1.4169052e-003 , -9.6388816e-004 ,  7.1310304e-004 , -3.8520650e-004 , -4.0732884e-003 , -2.7762071e-003 ,  4.0462353e-003 ,  6.6871000e-003 , 
                  -2.2464560e-017 , -7.4035031e-003 , -5.0384904e-003 ,  4.0362308e-003 ,  7.4672547e-003 ,  1.0643788e-003 , -5.9936730e-003 , -4.6407132e-003 ,  
                  2.1724849e-003 ,  5.0518255e-003 ,  1.2843847e-003 , -3.0469159e-003 , -2.6430721e-003 ,  6.2995158e-004 ,  2.0346089e-003 ,  6.5911624e-004 , 
                  -7.7005318e-004 , -6.2339213e-004 ,  3.3743632e-005 ,  5.0633916e-005 , -1.0493663e-004 ,  2.2784377e-004 ,  5.1009407e-004 ,  3.1681939e-005 , 
                  -6.7060244e-004 , -5.2325836e-004 ,  3.8234364e-004 ,  8.1777468e-004 ,  1.6205395e-004 , -7.0917230e-004 , -6.3251873e-004 ,  2.7195643e-004 ,  
                  7.9515685e-004]
        
    def __init__(self, blackboard, pattern):
        """
        @param blackboard:
            blackboard instance which contains the data that must be plotted.
        @param pattern
            the pattern corresponding to the data buffer that must be filtered. Only one pattern should be selected.
        """
        if isinstance( pattern, list ):
            if len( pattern ) == 1:
                pattern = pattern[0]
        if not isinstance( pattern, basestring ):
            raise TypeError( 'Incompatible pattern type. Should be a single string.' )
        
        DataConsumer.__init__(self, blackboard, [pattern])
        self.buffer1 = [ 0 for _ in range(len(self.coefLPF256))]
        self.buffer2 = [ 0 for _ in range(len(self.coefBSF256))]
    
    def _process_data(self, pattern, data, timestamps ):
        """
        Inherited from DataConsumer.
        First applies the band stop filter, the the low pass filter
        
        @param pattern
            The pattern corresponding to the data's buffer
        @param data
            The new data samples, which are not processed yet.
        """
        for d in data:
            dat = d
            
            self.buffer2 = (self.buffer2 + [dat])[-len(self.coefBSF256):]
            dat = sum( [ x*y for x,y in zip( self.buffer2, self.coefBSF256) ] )

            self.buffer1 = (self.buffer1 + [dat])[-len(self.coefLPF256):]
            dat = sum( [ x*y for x,y in zip( self.buffer1, self.coefLPF256) ] )

            self.blackboard.put_data(pattern+'/pp', dat )
        