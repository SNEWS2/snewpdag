'''
Unit tests for DistCalc1, DistCalc2, MeanDist and DistNormalizer plugins
'''

import unittest
from snewpdag.dag import Node
from snewpdag.plugins import DistCalc1
from snewpdag.plugins import DistCalc2 
from snewpdag.plugins import MeanDist
from snewpdag.plugins import DistNormalizer

class TestDistCalc(unittest.TestCase):

    def test_plugin0(self):
        print('-----Test 1-----')

        h1 = DistCalc1('IceCube, NO', 'n', 'dist', 100, name = 'dist0')
        h2 = DistCalc2('IceCube, NO', 'n', 'dist', 100, name = 'dist1')
        h3 = MeanDist('IceCube, NO', 'n', 'dist', 100, 'Histogram', name = 'dist2')

        temp = []
        bg_temp = 100 #background count
        for i in range(0,100):
            temp.append(0)
        for i in range(100,150):
            temp.append(20)
        for i in range(150,200):
            temp.append(0)
        for i in range(200,250):
            temp.append(60)
        
        temp = [i+bg_temp for i in temp] #constant background
        data = { 'n': temp }

        self.assertAlmostEqual(h1.dist_calc1(data)[0], 30.28194228)
        self.assertAlmostEqual(h1.dist_calc1(data)[1], 2.58136852)

        self.assertAlmostEqual(h2.dist_calc2(data)[0], 34.93321729)
        self.assertAlmostEqual(h2.dist_calc2(data)[1], 1.34000000)

        self.assertAlmostEqual(h3.mean_dist(data)[0], 33.94589411)
        self.assertAlmostEqual(h3.mean_dist(data)[1], 1.18930615)
    
    def test_plugin1(self):
        print('-----Test 2-----')
        h1 = DistNormalizer(4.0, 'n', 'n_norm', name='dist0')

        data = { 'n': 5.0 }

        print(h1.dist_normalizer(data))

    
    def test_plugin2(self):
        print('-----Test 3-----')
        h1 = MeanDist('IceCube, NO', 'n', 'dist', 100, 'Error', name = 'dist2')

        temp = []
        bg_temp = 100 #background count
        for i in range(0,100):
            temp.append(0)
        for i in range(100,150):
            temp.append(20)
        for i in range(150,200):
            temp.append(0)
        for i in range(200,250):
            temp.append(60)
        
        temp = [i+bg_temp for i in temp] #constant background
        data = { 'n': temp }

        h1.mean_dist(data)
    