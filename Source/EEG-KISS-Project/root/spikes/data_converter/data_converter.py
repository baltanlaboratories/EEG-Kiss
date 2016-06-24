'''
Created on 8 mei 2015

@author: Bas.Kooiker
'''
import csv
import numpy as np

from root.data import filenames
from root.input.hdfreader import HDFReader

def main():
    reader = HDFReader()
    for i,duo in enumerate(filenames):
        if i != 4:
            for j,filename in enumerate(duo):
                print filename
                [ dat, _ ] = reader.read( filename )
                dat = [ np.asarray( dat[x][ 1 ] ) for x in range(4) ]
                print i,j
                with open('data_%d_%d.csv'%(i,j), 'wb') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|')
                    
                    for row_nr in range( len(dat[0]) ):
                        row = [ dat[v][row_nr] for v in range(4) ]
    #                     print row
                        spamwriter.writerow( row )
            


if __name__ == '__main__':
    main()