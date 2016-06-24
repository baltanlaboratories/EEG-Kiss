'''
Created on 11 mei 2015

@author: Bas.Kooiker
'''

from distutils.core import setup
import py2exe

import matplotlib

import glob

opts = {
    'py2exe': { 'includes' : ["matplotlib.backends",  
                              "matplotlib.figure",
                              "h5py",
                              "pylab", 
                              "numpy", 
                              "matplotlib.backends.backend_tkagg",
                              "matplotlib.backends.backend_qt4agg",
                              'root',
                              'pip',
							  ],
                'excludes': ['_qt4agg'],
                'dll_excludes': ['libgdk-win32-2.0-0.dll',
                                 'libgobject-2.0-0.dll'],
                'packages' : [	'matplotlib',
								'h5py',
								'scipy',
								'matplotlib.backends.backend_tkagg',
								'pip',
							 ] 
              }
       }

data_files = [(r'mpl-data', glob.glob(r'C:\Python27EEG\Lib\site-packages\matplotlib\mpl-data\*.*')),
              (r'mpl-data', [r'C:\Python27EEG\Lib\site-packages\matplotlib\mpl-data\matplotlibrc']),
              (r'mpl-data\stylelib',glob.glob(r'C:\Python27EEG\Lib\site-packages\matplotlib\mpl-data\stylelib\*.*')),
              (r'mpl-data\images',glob.glob(r'C:\Python27EEG\Lib\site-packages\matplotlib\mpl-data\images\*.*')),
              (r'mpl-data\fonts',glob.glob(r'C:\Python27EEG\Lib\site-packages\matplotlib\mpl-data\fonts\*.*')),
			  ]

data_files = matplotlib.get_py2exe_datafiles()

setup(windows=[{"script" : "root/gui/applicationmain.py"}], options=opts,   data_files=data_files)





setup(console=['gui/applicationmain.py'])