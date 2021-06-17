'''
Unit test for DistanceCal plugin
'''
import unittest
import numpy as np
from snewpdag.dag import Node
from snewpdag.plugins import DistanceCal

class TestDistanceCal(unittest.TestCase):

    def test_plugin0(self):
        h = DistanceCal(name = 'dist0')
        data = [12000, 36000]
        self.assertAlmostEqual(h.dist_ratio(data[0]), 9.128709292)
        self.assertAlmostEqual(h.f_delta(data), 3.0)
        self.assertAlmostEqual(h.findDist(data), 9.128709292)