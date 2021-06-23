'''
Unit test for DistanceCal plugin
'''
import unittest
import numpy as np
from snewpdag.dag import Node
from snewpdag.plugins import DistanceRatio
from snewpdag.plugins import DistanceFit

class TestDistanceCal(unittest.TestCase):

    def test_plugin0(self):
        h = DistanceRatio(name = 'dist0')
        h2 = DistanceFit(name = 'dist0')
        data = [
            [12000, 36000],
            [10000, 27000],
            [11000, 29700],
            [9000, 20700],
        ]                                   # [1]: N(100 - 150 ms); [0]: N(0 - 50 ms)
        data_error = [
            [11, 25],
            [13, 18],
            [20, 30],
            [8, 21],
        ]
        self.assertAlmostEqual(h.dist_ratio(data[0][0]), 9.128709292)
        self.assertAlmostEqual(h.dist_error(data[0][0], data_error[0][0]), 0.912891928)

        self.assertAlmostEqual(h2.f_delta(data[0]), 3.0)
        self.assertAlmostEqual(h2.f_delta(data[1]), 2.7)
        # print(h2.linear_fit(data))
        # (m, c) = (0.00021000000000000033, 0.46999999999999786)
        # print(h2.constrain_dist(data, data_error))
        dist, dist_error = h2.constrain_dist(data, data_error)
        self.assertAlmostEqual(dist[0], 9.110650502)
