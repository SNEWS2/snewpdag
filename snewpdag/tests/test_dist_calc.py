'''
Unit tests for DistCalc1 and DistCalc2 plugins
'''

import unittest
from snewpdag.dag import Node
from snewpdag.plugins import DistCalc1
from snewpdag.plugins import DistCalc2 

class TestDistCalc(unittest.TestCase):

    def test_plugin0(self):
        h1 = DistCalc1('IceCube, NO', name = 'dist0')
        h2 = DistCalc2('IceCube, NO', name = 'dist1')

        data = [1000, 2500] # [N(0-50ms), N(100-150ms)]

        self.assertAlmostEqual(h1.dist_calc1(data), 30.28194228)
        self.assertAlmostEqual(h2.dist_calc2(data), 30.75068122)