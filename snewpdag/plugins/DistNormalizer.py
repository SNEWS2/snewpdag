'''
This plugin normalise the counts from the signal file(10kpc) according to the true distance 

assuming that the measured count obeys inverse square law

Data assumptions:
    - 1 ms binning
    - first 100 bins of each data have no SN emission (for background calculation)


Constructor arguments: 
    true_dist: (kpc)
    in_field: string, "n",
              to get the count numbers from data["n"]
    out_field: string, "n_norm" (as an example),
              used for adding/updating the field in the data dict

Output json:
    alert:
        add normalised count
              
'''

import logging
import numpy as np
from snewpdag.dag import Node
        

class DistNormalizer(Node):
    def __init__(self, true_dist, in_field, out_field,**kwargs):
        self.true_dist = true_dist
        self.in_field = in_field
        self.out_field = out_field
        super().__init__(**kwargs)

    def dist_normalizer(self, data):
        n_norm = data[self.in_field]*(10/self.true_dist)**2
        
        return n_norm
    
    def alert(self, data):
        n_norm = self.dist_normalizer(data)
        d = { self.out_field: (n_norm) }
        data.update(d)
        return True
        
        
