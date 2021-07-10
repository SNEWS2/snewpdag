
'''
This plugin calculates the weighted mean distance using the estimated distances found by the dist_calc1 and dist_calc2
methods, with the weights corresponding to the statistical and systematic errors

Data assumptions:
    - 0.1 ms binning
    - first 1000 bins of each data have no SN emission (for background calculation)

Constructor arguments: 
    detector: string, "detector name, ordering" ,
              one of ["IceCube, NO","IceCube, IO","HK, NO","HK, IO","SK, NO","SK, IO",
              "DUNE, NO","DUNE, IO","JUNO, NO","JUNO, IO"]
              
'''

import logging
import numpy as np
from snewpdag.dag import Node
from snewpdag.plugins import DistCalc1
from snewpdag.plugins import DistCalc2

class MeanDist(Node):
    
    def __init__(self, detector, **kwargs):
        self.DistCalc1 = DistCalc1(detector)
        self.DistCalc2 = DistCalc2(detector)        
        super().__init__(**kwargs)
    
    def mean_dist(self, data):
        dist1, dist1_err = self.DistCalc1.dist_calc1(data)
        dist2, dist2_err = self.DistCalc2.dist_calc2(data)
        
        mdist = (dist1/dist1_err**2 + dist2/dist2_err**2)/ (1.0/dist1_err**2+1.0/dist2_err**2)
        mdist_err = 1.0/np.sqrt(1.0/dist1_err**2+1.0/dist2_err**2)
    
        return mdist, mdist_err
