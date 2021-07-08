'''
This plugin estimate the distance to the supernova from the neutrino data by constraining the progenitor
assuming one-to-one correspondence bt f_delta and N50_exp (expected 0-50ms count) (f_delta = m*N50_exp + b)

Constructor arguments: 
    detector: string, "detector name, ordering" ,
              one of ["IceCube, NO","IceCube, IO","HK, NO","HK, IO","SK, NO","SK, IO",
              "DUNE, NO","DUNE, IO","JUNO, NO","JUNO, IO"]
              
'''

import logging
import numpy as np
from snewpdag.dag import Node


class DistCalc2(Node):
    
    def _init_(self, detector,**kwargs)
        self.detector = detector
        super().__init__(**kwargs)
    
    def dist_calc2(self,data)
        #dict of f_delta-N50 fit parameters at 10kpc
        #{'detector, ordering': [m, b, progenitor model variance]}
        fit_par = {'IceCube, NO': [0.000182, 0.779, 0.11], \
               'IceCube, IO': [0.000125, 0.342, 0.0656], \
               'HK, NO': [0.00152, 0.894, 0.0973], \
               'HK, IO': [0.00119, 0.439, 0.0529], \
               'SK, NO': [0.0105, 0.894, 0.0973], \
               'SK, IO': [0.00815, 0.439, 0.0529], \
               'DUNE, NO': [0.0158, -0.0304, 0.0641], \
               'DUNE, IO': [0.00978, -0.706, 0.0411], \
               'JUNO, NO': [0.0109, 0.746, 0.0909], \
               'JUNO, IO': [0.0088, 0.319, 0.0515]}
        
        #N50 = data[50]
        
        #f_delta = (data[150]-data[100])/data[50]
        f_delta = 2.5
        m = fit_par[self.detector][0]
        b = fit_par[self.detector][1]
        N50_exp = (f_delta-b)/m
        
        dist2 = np.sqrt(N50_exp*10**2/N50)
        
        
        
    return dist2
