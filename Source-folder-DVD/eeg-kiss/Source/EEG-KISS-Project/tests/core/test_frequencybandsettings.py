import unittest
import Tkinter as tk

from random                 import randint
from root.core.settings     import FrequencyBandSettings 

class TestFrequencyBandSettings(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk('EEG kiss')

    """ Test getCopy functionality of the FrequencyBandSettings  """
    def test_frequencybandsettings_getcopy(self):
        # For now only focus on code coverage
        frequencybandsettings = FrequencyBandSettings()

        self.assertIsNotNone(frequencybandsettings.getCopy())
        
    """ Test update functionality of the FrequencyBandSettings  """
    def test_frequencybandsettings_update(self):
        # For now only focus on code coverage
        frequencybandsettings = FrequencyBandSettings()

        # The settings class should be improved! 
        # Direct access to members is used. This is bad practice.
        # Pass a new dictionary (or 2 dictionaries) to the function to improve quality
        frequencybandsettings.update(frequencybandsettings)
        
    """ Test get_showLabels functionality of the FrequencyBandSettings  """
    def test_frequencybandsettings_get_showlabels(self):
        # For now only focus on code coverage
        frequencybandsettings = FrequencyBandSettings()

        self.assertTrue( frequencybandsettings.get_showLabels() )

        # Ugly, but needed since the settingsclass should be improved!
        frequencybandsettings.showLabels.set(0)

        self.assertFalse( frequencybandsettings.get_showLabels() )
                
    def tearDown(self):
        unittest.TestCase.tearDown(self)

if __name__ == '__main__':
    unittest.main()
