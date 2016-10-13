import unittest
import Tkinter as tk

from random                 import randint
from root.core.constants    import ChannelTypes, FrequencyBands
from root.core.settings     import TimeSettings

class TestTimeSettings(unittest.TestCase):

    def setUp(self):
        #return super(TestSettings, self).setUp()
        self.root = tk.Tk('EEG kiss')

    """ Test getCopy functionality of the TimeSettings  """
    def test_timesettings_getcopy(self):
        # For now only focus on code coverage
        timesettings = TimeSettings()

        self.assertIsNotNone(timesettings.getCopy())
        
    """ Test update functionality of the TimeSettings  """
    def test_timesettings_update(self):
        # For now only focus on code coverage
        timesettings = TimeSettings()

        # The settings class should be improved! 
        # Direct access to members is used. This is bad practice.
        # Pass a new dictionary (or 2 dictionaries) to the function to improve quality
        timesettings.update(timesettings)
        
    """ Test get_showLabels functionality of the TimeSettings  """
    def test_timesettings_get_showlabels(self):
        # For now only focus on code coverage
        timesettings = TimeSettings()

        self.assertTrue( timesettings.get_showLabels() )

        # Ugly, but needed since the settingsclass should be improved!
        timesettings.showLabels.set(0)

        self.assertFalse( timesettings.get_showLabels() )
                
    def tearDown(self):
        unittest.TestCase.tearDown(self)

if __name__ == '__main__':
    unittest.main()
