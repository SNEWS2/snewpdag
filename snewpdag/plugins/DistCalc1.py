'''
This plugin estimate the distance to the supernova from the neutrino data and IMF weighted

assuming that the measured count obeys inverse square law

Constructor arguments: 
    detector: string, "detector name, ordering" ,
              one of ["IceCube, NO","IceCube, IO","HK, NO","HK, IO","SK, NO","SK, IO",
              "DUNE, NO","DUNE, IO","JUNO, NO","JUNO, IO"]
              
'''

import logging
import numpy as np
from snewpdag.dag import Node


class DistCalc1(Node):
    
    def __init__(self, detector, **kwargs):
        self.detector = detector
        super().__init__(**kwargs)
    
    def dist_calc1(self, data):
        # data: [N(0-50ms), N(100-150ms)]
        # dict of IMF weighted 0-50ms signals and errors
        # {'detector, ordering': [IMF signal, error, frac error]}
        IMF_signal = {'IceCube, NO': [9169.96028097276, 1536.248563196319, 0.1675305580531208], \
               'IceCube, IO': [10773.835720043031, 1619.9659745788326, 0.15036111712425132], \
               'HK, NO': [916.1876727055476, 152.3796730871074, 0.16631927892799808], \
               'HK, IO': [963.8751402143208, 140.05882795055814, 0.14530806129040283], \
               'SK, NO': [133.2636614844433, 22.16431608539741, 0.16631927892799786], \
               'SK, IO': [140.20002039481017, 20.372193156444798, 0.1453080612904028], \
               'DUNE, NO': [97.57634394839303, 13.777694691000772, 0.14119912812359142], \
               'DUNE, IO': [161.09154447956922, 17.119642804057936, 0.10627275850737883], \
               'JUNO, NO': [128.54796152661447, 20.633251789516653, 0.16051014379753317], \
               'JUNO, IO': [135.26455501942974, 18.91887993385422, 0.13986576107197238]}

        N50 = data[0]
        dist_par = 10.0
        dist1 = dist_par*np.sqrt(IMF_signal[self.detector][0]/N50)
        
        return dist1
