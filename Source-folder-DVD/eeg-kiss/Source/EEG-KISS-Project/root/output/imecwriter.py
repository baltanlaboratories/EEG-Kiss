import os
import time

import h5py

class IMECWriter:
    
    """
    This class is responsible for creating HDF5 files.
    It can create a file according to the IMEC layout, add attributes to the metadata of a group 
    and add a dataset (like EEG-1) to a group.
    """
    
    def __init__( self ):
    
        self.writeFile = None
    
    def createEEGFile(self, name):
        """ 
        This function creates an HDF5 file and adds groups to it to conform to the IMEC format.
        @param name: a string that represents the name of the file to be created.
        """
        
        base_dir = os.path.dirname(__file__) + "\\..\\..\\..\\"
        dir = base_dir + "records\\"
        
        if not os.path.exists(dir) :
            os.mkdir( dir )
 
        # Check text-file with sub-foldername
        subfolderfile = base_dir + "subfolder.txt"
        if os.path.exists(subfolderfile):
            file = open(subfolderfile, 'r')
            dir += file.read() + "\\"
        
        if not os.path.exists(dir) :
            os.mkdir( dir )
        
        datetime = time.strftime("%y%m%d_%H%M%S")
        
        filePath = dir + datetime + '_' + name + '.hdf5'
#         if os.path.isfile(filePath) : 
#             dupNum = 1
#             while os.path.isfile(filePath) : 
#                 fullName = name + '(' + str( dupNum ) + ')'
#                 filePath = dir + fullName + '.hdf5'
#                 dupNum += 1
        
        self.writeFile = h5py.File( filePath, 'w') # create a new file
        
        grpEvent = self.writeFile.create_group('Event')
        grpEvent.attrs['sid'] = [4398046511104] # filled with dummy data.
        
        grpNode = self.writeFile.create_group('Node')
        grpNode.attrs['sid'] = [5497558138880] # filled with dummy data.
        
        grpSignal = self.writeFile.create_group('Signal')
        grpSignal.attrs['epoch'] = [1411760234296] # filled with dummy data.
        
        grpNode.create_dataset('data', (92,), dtype='i')
        
        grpSignal.create_group( 'Markers' )

        #create the group nodes for each data type and each channel
        for i in range(1, 9):
            grpSignal.create_group( 'DC-' + str( i ) )
            grpSignal.create_group( 'EEG-' + str( i ) )
            grpSignal.create_group( 'EEGA-' + str( i ) )
            grpSignal.create_group( 'ImpI-' + str( i ) )
            grpSignal.create_group( 'ImpIQ-' + str( i ) )
            grpSignal.create_group( 'ImpQ-' + str( i ) )

    def _setSignalAttributes(self, grpInput, begin, end, freq, sid):
        """
        Add the attribute fields and give them the values passed in the parameters.
        @param grpInput: the group node for which to change the attributes.
        @param begin: ?
        @param end: ?
        @param freq: the frequency for the channel that the group represents
        @param sid: ?
        """
        grpInput.attrs['begin'] = [begin]
        grpInput.attrs['end'] = [end]
        grpInput.attrs['freq'] = [freq]
        grpInput.attrs['sid'] = [sid]

    def write(self, dataType, channel, frequency, dataArray ):
        """
        This function writes the actual data for a given channel. 
        The dataType & channel must be correct for a write to succeed.
        @param dataType: the type of data (for example: EEG)
        @param channel: the channel number (1 to 8)
        @param frequency: the frequency for the given group
        @param dataArray: the array of data that should be written to the group  
        """
        grpName = dataType + '-' + str(channel)
        grpWriteSignal = self.writeFile.get('Signal/' + grpName )
        
        if grpWriteSignal != None:
#             print 'print path: ' + grpWriteSignal.name
            
            # group filled with the passed frequency and dummy data:
            self._setSignalAttributes( grpWriteSignal, 0.0, 342.296875, frequency, 18014398526324745 ) 
            
            # add the data (array) to the node.
            grpWriteSignal.create_dataset('data', data=dataArray )
        else:
            print 'invalid type (%s) or channel (%s) passed to write function' % (dataType, channel)

    def write_markers(self, markers):
        grpName = 'Markers'
        grpWriteSignal = self.writeFile.get('Signal/' + grpName )
        if grpWriteSignal != None:
#             print 'write_markers() -> path: ' + grpWriteSignal.name
            grpWriteSignal.create_dataset('data', data=markers )
        else:
            print 'No markers-group created!'

    def closefile(self):
        """ 
        This function closes the file that is created in this class
        """
        if self.writeFile != None:
#             print 'closing file'
            self.writeFile.close()
        