'''
Using the property that count number is proportional to (distance)^2.

This plugin is for calculating the distance of a supernova using neutrino data.
'''

import numpy as np
from snewpdag.dag import Node

class DistanceRatio(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # N1 / N2 = (d2 / d1)^2
    def dist_ratio(self, data):
        # placeholder values
        N1 = 10000  # 10000 counts (standard candle)
        d1 = 10     # 10 kpc

        # data = N2
        d2 = np.sqrt(N1 / data) * d1
        return d2

    def dist_error(self, data, data_error):
        # placeholder values
        N1 = 10000  # 10000 counts (standard candle)
        d1 = 10     # 10 kpc
        N1_error = 10
        d1_error = 1

        # general propagation of error
        d2 = self.dist_ratio(data)
        d2_error = d2 * np.sqrt( (d1_error/d1)**2 + (N1_error/2/N1)**2 + (data_error/2/data)**2 )

        return d2_error
