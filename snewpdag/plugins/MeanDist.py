
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
    in_field: string, "count",
              to get the count numbers from data["count"]
    out_field: string, "dist" (as an example),
              used for adding/updating the field in the data dict
              
'''

import logging
import numpy as np
from snewpdag.dag import Node
from snewpdag.plugins import DistCalc1
from snewpdag.plugins import DistCalc2

class MeanDist(Node):
    
    def __init__(self, detector, in_field, out_field, **kwargs):
        self.detector = detector
        self.in_field = in_field
        self.out_field = out_field
        super().__init__(**kwargs)
    
    def mean_dist(self, data):
        h1 = DistCalc1(self.detector, self.in_field, self.out_field, name = self.name)
        h2 = DistCalc2(self.detector, self.in_field, self.out_field, name = self.name)  

        dist1, dist1_err = h1.dist_calc1(data)
        dist2, dist2_err = h2.dist_calc2(data)
        
        mdist = (dist1/dist1_err**2 + dist2/dist2_err**2)/ (1.0/dist1_err**2+1.0/dist2_err**2)
        mdist_err = 1.0/np.sqrt(1.0/dist1_err**2+1.0/dist2_err**2)
    
        return mdist, mdist_err

    def alert(self, data):
        mdist, mdist_err = self.mean_dist(data)
        d = { self.out_field: [mdist, mdist_err] }
        data.update(d)
        return True
    
    def revoke(self, data):
        return True

    def reset(self, data):
        return True

    def report(self, data):
        return True