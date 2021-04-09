"""
Unit tests for OutputMap node
"""
import unittest
import numpy as np
import healpy as hp
from snewpdag.dag import Node
from snewpdag.plugins import OutputMap

class TestOutputMap(unittest.TestCase):
    
    def test_(self):
        n1 = OutputMap(name='n1')
        data = [{'action': 'alert','res': 128, 'r':np.array([[2.39459173, 0.63233279],[-1.81165176,  0.77405352]]), 'errs': np.array([[0.        , 0.01016553],[0.01016553, 0.        ]]), 'biases': np.array([[ 0.000e+00, -8.659e-05], [ 8.659e-05,  0.000e+00]]),'loc': np.array([-1.64759081, -0.50474922])}] #sk and dune
        n1.update(data)
        
        self.assertEqual(n1.last_data['m'][600],1)
        self.assertEqual(n1.last_data['m'][1083],1)
        self.assertEqual(n1.last_data['m'][200],2)
        self.assertEqual(n1.last_data['m'][1200],2)
        self.assertEqual(n1.last_data['m'][227],3)
        self.assertEqual(n1.last_data['m'][11756],3)
