'''
TrueDist: generates a true distance to the SN upon an alert, either specified or randomly chosen from a list

Constructor arguments:
    sn_distance: distance to source (in kpc) or "Random", 
                then a distance is randomly chosen from a list that can be specify (default: 60 evenly spaced distances between 1 and 30)
    d_lo: (only if sn_distance="random") lower bound of the list (default: 1)
    d_hi: (only if sn_distance="random") upper bound of the list (default: 25)
    d_no: (only if sn_distance="random") # of evenly spaced values in the list (default: 25)

'''

import logging
import numpy as np
from snewpdag.dag import Node

class TrueDist(Node):

    def __init__(self, sn_distance, **kwargs):
        self.d_lo = kwargs.pop('d_lo', 1)
        self.d_hi = kwargs.pop('d_hi', 25)
        self.d_no = kwargs.pop('d_no', 25)
        self.input = sn_distance
        super().__init__(**kwargs)

    def alert(self, data):
        if self.input == 'Random':
            dist_list = np.linspace(self.d_lo, self.d_hi, num=self.d_no, endpoint=True)
            sn_distance = Node.rng.choice(dist_list, replace=True, shuffle=False)
            d2 = { 'd_lo': (self.d_lo), 'd_hi': (self.d_hi), 'd_no': (self.d_no) }
            data.update(d2)
            #logging.info('sn_distance = {0} chosen randomly from {1} values between {2} and {3} inclusively'.format(sn_distance,self.d_no,self.d_lo,self.d_hi))
        elif isinstance(self.input, (float, int)):
            sn_distance =  self.input
            #logging.info('sn_distance = {}'.format(sn_distance))
        d1 = { 'sn_distance': (sn_distance) }
        data.update(d1)

        return True

    def report(self, data):
        d1 = { 'sn_distance': (self.input) }
        data.update(d1)
        if self.input == 'Random':
            d2 = { 'd_lo': (self.d_lo), 'd_hi': (self.d_hi), 'd_no': (self.d_no) }
            data.update(d2)

        return True