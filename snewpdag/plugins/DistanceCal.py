'''
Using the method of Segerlund, O'Sullivan, O'Connor from the paper
'Measuring the Distance and ZAMS Mass of Galactic Core-Collapse Supernovae Using Neutrinos'.

This plugin is for calculating the distance of a supernova using neutrino data.
'''

import logging
import numpy as np
import healpy as hp
from snewpdag.dag import Node

class DistanceCal(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # N1 / N2 = (d2 / d1)^2
    def dist_ratio(self, data):
        N1 = 10000  # 10000 counts (standard candle)
        d1 = 10     # 10 kpc
        # data = N2
        d2 = np.sqrt(N1 / data) * d1
        return d2

    # data[1] = N(100 - 150 ms); data[0] = N(0 - 50 ms)
    def f_delta(self, data):
        return data[1]/data[0]
    
    # use linear relationship between f_delta and N(0-50 ms) to find the distance using f_delta
    def findDist(self, data):
        slope = 0.0001875 # placeholder
        y_intercept = 0.75 # placeholder
        f_delta = self.f_delta(data)
        # f_delta = slope * data[0] + y_intercept
        data[0] = (f_delta - y_intercept) / slope
        return self.dist_ratio(data[0])
