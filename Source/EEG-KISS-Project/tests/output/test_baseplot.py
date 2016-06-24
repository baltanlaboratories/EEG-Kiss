import unittest 
import matplotlib.pyplot                as plt

from root.core.blackboard               import Blackboard
from root.input.datagenerator           import DataGenerator
from root.output.baseplot               import BasePlot
from time                               import sleep

class TestBasePlot(unittest.TestCase):

    def setUp(self):        
        self.bb = Blackboard()
        self.pattern = "/foo"
        self._fig, self._ax = plt.subplots( 1 )
        
    def test_init_no_blackboard(self):

        with self.assertRaises(ValueError):
            BasePlot("foo", [self.pattern], self._ax)

    def test_update_ax(self):
        baseplot = BasePlot(self.bb, [self.pattern], self._ax)

        with self.assertRaises(NotImplementedError):
            baseplot._update_ax()

    def test_process_plot_data(self):
        baseplot = BasePlot(self.bb, [self.pattern], self._ax)

        with self.assertRaises(NotImplementedError):
            baseplot._process_plot_data(None, None, None)

    def test_process_data(self):

        offset         = 5000
        frequencies    = [1,3,5,7]
        amps           = [1,2,1,8]

        baseplot = BasePlot(self.bb, [self.pattern], self._ax)
        baseplot._process_plot_data = fake_function

        gen      = DataGenerator( self.bb, self.pattern, frequencies=frequencies, amplitudes=amps, offset=offset, noise=0 )

        self.bb.set_bufsize( self.pattern, 128 )

        gen.start() 

        baseplot.start()

        sleep(10)

        baseplot.stop()
        gen.stop

    def tearDown(self):
        unittest.TestCase.tearDown(self)

def fake_function(pattern, data, timestamps):
    pass

if __name__ == '__main__':
    unittest.main()
