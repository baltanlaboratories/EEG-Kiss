# -*- coding: utf-8 -*-
"""
Abstract filereader as interface class meant for serve as a basis for multiple data input units.
Every filereader will at least have one method 'read()'.
The filereaders will be used to load pre-recorded data from disk for offline analysis or data simulations. 
"""

class AbstractFilereader ( object ):
    
    @staticmethod
    def read( self, filename ):
        raise NotImplementedError