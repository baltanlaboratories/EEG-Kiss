import unittest 

from root.core.blackboard               import Blackboard
from root.processing.arousalprocessing  import ArousalProcessor
from root.core.constants                import PatternStrings, VisualisationTypes

class TestArousalProcessing(unittest.TestCase):

    def setUp(self):        
        self.nr_of_headsets = 2
        self.channels       = [1,2,3,4]
        self.processors     = []

        self.bb = Blackboard()

        patterns = []
        for channel in [1,3]:
            for freq in [PatternStrings.ALPHA, PatternStrings.BETA]:
                patterns.append(PatternStrings.SIGNAL_EEG + '%d' % (1) + PatternStrings.CHANNEL + '%d' % (channel) + freq)

        self.processor = ArousalProcessor( self.bb, patterns)
        
    def test_init_arousalprocessing_pattern_no_channel(self):

        with self.assertRaises(ValueError):
            ArousalProcessor( self.bb, ['foo', 'foo', 'foo', 'foo'])

    def test_set_calculation_type(self):

        self.processor.set_calculation_type("test")

    def test_calculate_arousal(self):

        test_value = 1

        self.assertEqual(self.processor.calculate_arousal(test_value, test_value, test_value, test_value), test_value)

    def test_calculate_arousal_value_error(self):

        test_value = 1

        with self.assertRaises(ValueError):
            self.processor.calculate_arousal(test_value, test_value, test_value, False)

    def test_calculate_valence_error(self):

        test_value  = 1
        test_result = (test_value/test_value)-(test_value/test_value)

        self.assertEqual(self.processor.calculate_valence(test_value, test_value, test_value, test_value),test_result)

    def test_calculate_valence_error(self):

        test_value = 1

        with self.assertRaises(ValueError):
            self.processor.calculate_valence(test_value, test_value, test_value, False)

    def test_calculate(self):
        test_value          = 1
        test_result_valence = (test_value/test_value)-(test_value/test_value)

        self.processor.set_calculation_type(VisualisationTypes.AROUSEL)
        self.assertEqual(self.processor.calculate(test_value, test_value, test_value, test_value), test_value)

        self.processor.set_calculation_type(VisualisationTypes.VALENCE)
        self.assertEqual(self.processor.calculate(test_value, test_value, test_value, test_value), test_result_valence)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

if __name__ == '__main__':
    unittest.main()
