'''
DistCalc2: estimates the distance to the supernova from the neutrino data by constraining the progenitor
assuming one-to-one correspondence bt f_delta and N50_exp (expected 0-50ms count) (f_delta = m*N50_exp + b)

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


class DistCalc2(Node):

    # dict of f_delta-N50 fit parameters at 10kpc
    # {'detector, ordering': [m, b, progenitor model variance = b_err]}
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
    
    def __init__(self, detector, in_field, out_field, t0, **kwargs):
        self.in_field = in_field
        self.out_field = out_field
        self.t0 = t0
        self.detector = detector
        self.m = self.fit_par[self.detector][0]
        self.b = self.fit_par[self.detector][1]
        self.b_err = self.fit_par[self.detector][2]
        super().__init__(**kwargs)
    
    def dist_calc2(self, data):
        bg = np.mean(data[self.in_field][0: self.t0]) #averaged bins before t0 to find background
        N50 = np.sum(data[self.in_field][self.t0: self.t0+50]-bg) #N(0-50ms) corrected for background
        N50_err = np.sqrt(N50) #assume Gaussian
        N100_150 = np.sum(data[self.in_field][self.t0+100: self.t0+150]-bg) #N(100-150ms) corrected for background
        N100_150_err = np.sqrt(N100_150) #assume Gaussian
        f_delta = N100_150/N50
        f_delta_err = f_delta*np.sqrt((N50_err/N50)**2+(N100_150_err/N100_150)**2)
        
        dist_par = 10.0
        #m = self.fit_par[self.detector][0]
        #b = self.fit_par[self.detector][1]
        #b_err = self.fit_par[self.detector][2]
        m = self.m
        b = self.b
        b_err = self.b_err
        N50_exp = (f_delta-b)/m
        N50_exp_err = np.sqrt(f_delta_err**2+b_err**2)/m

        dist2 = dist_par*np.sqrt(N50_exp/N50)
        #dist2_err = 0.5*dist2*(np.sqrt((N50_err/N50)**2 + (N50_exp_err/N50_exp)**2))
        dist2_stats = np.sqrt((10.0**2/m)*((((N100_150-b*N50)**(0.5)*N50**(-2)+0.5*b*N50**(-1)*(N100_150-b*N50)**(-0.5))*N50_err)**2+((0.5*(N100_150-b*N50)**(-0.5)/N50)*N100_150_err)**2))
        dist2_sys = np.sqrt((5*N50**(-1)*m**(-0.5)*(N100_150-b*N50)**(-0.5)*N50)**2*(b_err)**2)
        dist2_err = np.sqrt(dist2_stats**2+dist2_sys**2)
        
        return (dist2, dist2_err, dist2_stats, dist2_sys, bg, N50, N100_150, m, b, b_err)

    def alert(self, data):
        (dist2, dist2_err, dist2_stats, dist2_sys, bg, N50, N100_150, m, b, b_err) = self.dist_calc2(data)
        d = { self.out_field: dist2, self.out_field+"_err": dist2_err, self.out_field+"_stats": dist2_stats, self.out_field+"_sys": dist2_sys, self.out_field+"background": bg, \
                self.out_field+"N50": N50, self.out_field+"N100_150": N100_150}
        data.update(d)
        return True
