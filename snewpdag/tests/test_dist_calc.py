'''
Unit tests for DistCalc1, DistCalc2 and MeanDist plugins
'''

import unittest
from snewpdag.dag import Node
from snewpdag.plugins import DistCalc1
from snewpdag.plugins import DistCalc2 
from snewpdag.plugins import MeanDist

class TestDistCalc(unittest.TestCase):

    def test_plugin0(self):
        h1 = DistCalc1('IceCube, NO', 'count', 'dist', name = 'dist0')
        h2 = DistCalc2('IceCube, NO', 'count', 'dist', name = 'dist1')
        h3 = MeanDist('IceCube, NO', 'count', 'dist', name = 'dist2')

        temp = []
        for i in range(0,1000):
            temp.append(0)
        for i in range(1000,1500):
            temp.append(2)
        for i in range(1500,2000):
            temp.append(0)
        for i in range(2000,2500):
            temp.append(6)
        data = { 'count': temp }

        self.assertAlmostEqual(h1.dist_calc1(data)[0], 30.28194228)
        self.assertAlmostEqual(h1.dist_calc1(data)[1], 2.58136852)

        self.assertAlmostEqual(h2.dist_calc2(data)[0], 34.93321729)
        self.assertAlmostEqual(h2.dist_calc2(data)[1], 1.34000000)

        self.assertAlmostEqual(h3.mean_dist(data)[0], 33.94589411)
        self.assertAlmostEqual(h3.mean_dist(data)[1], 1.18930615)