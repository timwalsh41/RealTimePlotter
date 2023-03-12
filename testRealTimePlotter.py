import unittest
from unittest.mock import Mock
from RealTimePlotter import RealTimePlotter

class RealTimePlotterTest(unittest.TestCase):
    def testNumRowsInput(self):
        with self.assertRaises(ValueError):
            plotter = RealTimePlotter(num_rows=2.7)

        with self.assertRaises(ValueError):
            plotter = RealTimePlotter(num_rows=-2)
    

    def testNumColsInput(self):        
        with self.assertRaises(ValueError):
            plotter = RealTimePlotter(num_cols=2.7)            
        
        with self.assertRaises(ValueError):
            plotter = RealTimePlotter(num_cols=-2)
    

    def testFigSizeInput(self):
        with self.assertRaises(ValueError):
            plotter = RealTimePlotter(fig_size=7)

        with self.assertRaises(ValueError):
            plotter = RealTimePlotter(fig_size=(1,2,3))

        with self.assertRaises(ValueError):
            plotter = RealTimePlotter(fig_size=("Frank","Reynolds"))

        with self.assertRaises(ValueError):
            plotter = RealTimePlotter(fig_size=(-1,-3))


    def testDisplayLenInput(self):        
        with self.assertRaises(ValueError):
            plotter = RealTimePlotter(display_len=2.7)            
        
        with self.assertRaises(ValueError):
            plotter = RealTimePlotter(display_len=-2)

    def testAddCurve(self):
        p = RealTimePlotter(num_rows=2, num_cols=2, display_len=100)
        p.add_curve()

