'''
DistCalc1: estimates the distance to the supernova from the neutrino data and IMF weighted

assuming that the measured count obeys inverse square law

Data assumptions:
    - 1 ms binning
    - first 100 bins of each data have no SN emission (for background calculation)


Constructor arguments: 
    detector: string, "detector name, ordering" ,
              one of ["IceCube, NO","IceCube, IO","HK, NO","HK, IO","SK, NO","SK, IO",
              "DUNE, NO","DUNE, IO","JUNO, NO","JUNO, IO"]
    in_field: string, "n",
              to get the count numbers from data["n"]
    out_field: string, "dist" (as an example),
              used for adding/updating the field in the data dict
    t0:       the "measured/estimated" time of the start of SN emission (ms)
              
'''

import logging
import numpy as np
from snewpdag.dag import Node
        

class DistCalc1(Node):
    
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
               'JUNO, IO': [135.26455501942974, 18.91887993385422, 0.13986576107197238], \
               'JUNO, MM': [681.8815065010299, 133.5332865244711, 0.19583063223062996], \
               'KM3, NO': [461.8162816532924, 77.39433329320009, 0.16758684430988452]}
    
    def __init__(self, detector, in_field, out_field, t0, **kwargs):
        self.in_field = in_field
        self.out_field = out_field
        self.t0 = t0
        self.detector = detector
        self.imf = self.IMF_signal[self.detector][0]
        self.imf_err = self.IMF_signal[self.detector][1]
        self.imf_ferr = self.IMF_signal[self.detector][2]
        super().__init__(**kwargs)
    
    def dist_calc1(self, data):
        bg = np.mean(data[self.in_field][0: self.t0]) #averaged bins before t0 to find background
        n50 = np.sum(data[self.in_field][self.t0: self.t0+50]) #uncorrected
        N50 = np.sum(data[self.in_field][self.t0: self.t0+50]-bg) #correct for background
        bg_err = np.sqrt(bg)
        n50_err = np.sqrt(n50)
        N50_err = np.sqrt(N50) #assume Gaussian
        
        dist_par = 10.0
        dist1 = dist_par*np.sqrt(self.imf/N50)
        #diff d1 wrt N50 or n50
        d = -5*self.imf**(0.5)*N50**(-1.5)
        dist1_stats = np.sqrt(d**2*(n50_err**2 + bg_err**2))
        #logging.info("{0} dist1_stats:{1}".format(self.name,dist1_stats))
        dist1_sys = 0.5*dist1*self.imf_ferr
        dist1_err = np.sqrt(dist1_stats**2+dist1_sys**2)
        return (dist1, dist1_err, dist1_stats, dist1_sys, bg, n50, N50, self.imf, self.imf_err)

    def alert(self, data):
        (dist1, dist1_err, dist1_stats, dist1_sys, bg, n50, N50, imf, imf_err) = self.dist_calc1(data)
        d = { self.out_field: dist1, self.out_field+"_err": dist1_err, self.out_field+"_stats": dist1_stats, self.out_field+"_sys": dist1_sys, \
                self.out_field+"background": bg, self.out_field+"N50": N50, self.out_field+"n50": n50}
        data.update(d)
        return True
