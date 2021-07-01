'''
Using the method of Segerlund, O'Sullivan, O'Connor
to constrain the count number.
Would combine data from many experiments.

This plugin is for constraining the neutrino data
and pass it to the DistanceRatio plugin to find the distance.
'''

import numpy as np
from snewpdag.dag import Node
from snewpdag.plugins import DistanceRatio

class DistanceFit(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def linear_fit(self, data):
        f = [] # f_delta array (the y-axis)
        N1 = [] # count num in 0-50ms (the x-axis)

        for i in range(0,len(data)):
            f.append(self.f_delta(data[i]))
            N1.append(data[i][0])
        
        m,c = np.polyfit(N1, f, 1) # linear fit (m = slope, c = y-intercept)
        return m,c
    
    # data[1] = N(100 - 150 ms); data[0] = N(0 - 50 ms)
    def f_delta(self, data):
        return data[1]/data[0]
    
    # use linear relationship between f_delta and N(0-50 ms) to find the distance using f_delta
    # this function returns an array
    def constrain_dist(self, data, data_error):
        '''
        slope = 0.0001875 # placeholder
        y_intercept = 0.75 # placeholder
        '''
        slope, y_intercept = self.linear_fit(data)
        h = DistanceRatio(name = 'dist0')

        dist = []
        dist_error = []
        for i in range(0, len(data)):
            f_delta = self.f_delta(data[i])
            # f_delta = slope * count_num + y_intercept
            count_num = (f_delta - y_intercept) / slope     # constrained count_num for 0-50 ms
            if count_num > 0:
                dist.append(h.dist_ratio(count_num))
                dist_error.append(h.dist_error(count_num, data_error[0][0]))

        return dist, dist_error