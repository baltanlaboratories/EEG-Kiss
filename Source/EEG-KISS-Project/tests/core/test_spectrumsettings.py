import unittest
import Tkinter as tk

from random                 import randint
from root.core.settings     import SpectrumSettings 

class TestSpectrumSettings(unittest.TestCase):

    def setUp(self):
        #return super(TestSettings, self).setUp()
        self.root = tk.Tk('EEG kiss')

    """ Test getCopy functionality of the SpectrumSettings  """
    def test_spectrumsettings_getcopy(self):
        # For now only focus on code coverage
        spectrumsettings = SpectrumSettings()

        self.assertIsNotNone(spectrumsettings.getCopy())
        
    """ Test update functionality of the SpectrumSettings  """
    def test_spectrumsettings_update(self):
        # For now only focus on code coverage
        spectrumsettings = SpectrumSettings()

        # The settings class should be improved! 
        # Direct access to members is used. This is bad practice.
        # Pass a new dictionary (or 2 dictionaries) to the function to improve quality
        spectrumsettings.update(spectrumsettings)
        
    """ Test get_showLabels functionality of the SpectrumSettings  """
    def test_spectrumsettings_get_showlabels(self):
        # For now only focus on code coverage
        spectrumsettings = SpectrumSettings()

        self.assertTrue( spectrumsettings.get_showLabels() )

        # Ugly, but needed since the settingsclass should be improved!
        spectrumsettings.showLabels.set(0)

        self.assertFalse( spectrumsettings.get_showLabels() )
                
    def tearDown(self):
        unittest.TestCase.tearDown(self)

if __name__ == '__main__':
    unittest.main()
