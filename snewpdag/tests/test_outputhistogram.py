'''
Unit tests for OutputHistogram plugin
'''
import unittest
import numpy as np
from snewpdag.dag import Node
from snewpdag.plugins import OutputHistogram

class TestOutputHistogram(unittest.TestCase):
    
    def test_plugin0(self):
        h1 = OutputHistogram(10, -0.1, 1.9, name = 'hist0')

        print('-----Test 1-----')
        data_freq = [ 0, 1, 1, 0, 1, 0, 0, 0, 0, 0 ] # frequency of each bin
        h1.plot_histogram(data_freq)
    
    def test_plugin1(self):
        h2 = OutputHistogram(10, -0.1, 1.9, index=1, name = 'hist1')

        print('-----Test 2-----')
        data_freq = [ [ 0, 1, 5, 0, 7, 0, 4, 0, 0, 0 ],
        [ 0, 1, 1, 8, 7, 4, 3, 2, 1, 0 ] ]
        h2.plot_histogram(data_freq)