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
    in_field: string, "n" or "n_norm",
              to get the count numbers from data["count"]
    out_field: string, "dist" or "dist_norm",
              used for adding/updating the field in the data dict
    t0:       the "measured/estimated" time of the start of SN emission (ms)
    mode:     string, either "Histogram" or "Error",
              "Histogram" if output is used to plot histogram for a fixed true distance,
              "Error" if output is used to plot errors against true distance

'''

import logging
import numpy as np
from snewpdag.dag import Node
from snewpdag.plugins import DistCalc1
from snewpdag.plugins import DistCalc2
from snewpdag.plugins import DistNormalizer

class MeanDist(Node):
    
    def __init__(self, detector, in_field, out_field, t0, mode, **kwargs):
        self.detector = detector
        self.in_field = in_field
        self.out_field = out_field
        self.t0 = t0
        self.mode = mode
        super().__init__(**kwargs)
    
    def mean_dist(self, data):
        h1 = DistCalc1(self.detector, self.in_field, self.out_field, self.t0, name = self.name)
        h2 = DistCalc2(self.detector, self.in_field, self.out_field, self.t0, name = self.name) 
        
        if self.mode == "Histogram":
            dist1, dist1_err = h1.dist_calc1(data)
            dist2, dist2_err = h2.dist_calc2(data)

            mdist = (dist1/dist1_err**2 + dist2/dist2_err**2)/ (1.0/dist1_err**2+1.0/dist2_err**2)
            mdist_err = 1.0/np.sqrt(1.0/dist1_err**2+1.0/dist2_err**2)
    
            return mdist, mdist_err
        
        elif self.mode == "Error":
            true_dist_array = np.linspace(4,40,100,endpoint=True)
            mdist_array = np.array([])
            mdist_err_array = np.array([])
            for i in range(100):
                h3 = DistNormalizer(true_dist_array[i], self.in_field, self.out_field, name = self.name)
                n_norm = h3.dist_normalizer(data)
                d = { self.in_field: n_norm }
                dist1, dist1_err = h1.dist_calc1(d)
                dist2, dist2_err = h2.dist_calc2(d)
                mdist = (dist1/dist1_err**2 + dist2/dist2_err**2)/ (1.0/dist1_err**2+1.0/dist2_err**2)
                mdist_err = 1.0/np.sqrt(1.0/dist1_err**2+1.0/dist2_err**2)
                mdist_array.np.append(mdist)
                mdist_err_array.np.append(mdist_err)
            return mdist_array, mdist_err_array
                
    
    def alert(self, data):
        mdist, mdist_err = self.mean_dist(data)
        if self.mode == "Histogram":
            d = { self.out_field: (mdist, mdist_err) }
            data.update(d)
        elif self.mode == "Error":
            d = { "mdist": (mdist), "mdist_err": (mdist_err) }
            data.update(d)
        return True
