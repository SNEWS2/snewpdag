'''
Unit test for DistanceCal plugin
'''
import unittest
import numpy as np
from scipy.stats import norm
from scipy.optimize import curve_fit
from snewpdag.dag import Node
from snewpdag.plugins import DistanceRatio
from snewpdag.plugins import DistanceFit
from snewpdag.plugins import GaussianFit

class TestDistanceCal(unittest.TestCase):

    def test_plugin0(self):
        print('-----Test 1-----')
        h = DistanceRatio(name = 'dist0')
        h2 = DistanceFit(name = 'dist0')
        # [1]: N(100 - 150 ms); [0]: N(0 - 50 ms)
        data = [
            [12000, 36000],
            [10000, 27000],
            [11000, 29700],
            [9000, 20700],
        ]               
        # arbitrary errors here, but in practice, we should use Gaussian fit to find the error (see test_plugin1)                    
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
    
    def test_plugin1(self):
        print('\n-----Test 2-----')
        h = GaussianFit(name = 'fit0')

        data = norm.rvs(10.0, 2.5, size=100)

        data_error = h.fit_error(data)
