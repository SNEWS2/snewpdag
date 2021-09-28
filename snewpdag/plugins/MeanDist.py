'''
MeanDist: calculates the weighted mean distance using the estimated distances found by the dist_calc1 and dist_calc2
methods, with the weights corresponding to the statistical and systematic errors

Data assumptions:
    - 1 ms binning
    - first 1000 bins of each data have no SN emission (for background calculation)

Constructor arguments: 
    detector: string, "detector name, ordering" ,
              one of ["IceCube, NO","IceCube, IO","HK, NO","HK, IO","SK, NO","SK, IO",
              "DUNE, NO","DUNE, IO","JUNO, NO","JUNO, IO"]
    in_field: string, e.g."n",
              to match "out_yfield" of SeriesBinner
    out_field: string, "dist",
              used for adding/updating the field in the data dict
    t0:       the "measured/estimated" time of the start of SN emission (ms)

'''

import logging
import numpy as np
from snewpdag.dag import Node
from snewpdag.plugins import DistCalc1
from snewpdag.plugins import DistCalc2

class MeanDist(Node):
    
    def __init__(self, detector, in_field, out_field, t0, **kwargs):
        self.detector = detector
        self.in_field = in_field
        self.out_field = out_field
        self.t0 = t0
        super().__init__(**kwargs)
    
    def mean_dist(self, data):
        h1 = DistCalc1(self.detector, self.in_field, self.out_field, self.t0, name = self.name)
        h2 = DistCalc2(self.detector, self.in_field, self.out_field, self.t0, name = self.name) 
    
        dist1, dist1_err, dist1_stats, dist1_sys, bg1, n50_1, N50_1, imf, imf_err = h1.dist_calc1(data)
        dist2, dist2_err, dist2_stats, dist2_sys, bg2, n50_2, N50_2, n100_150, N100_150, m, b, b_err = h2.dist_calc2(data)

        #calculate weighted mean
        mdist = (dist1/dist1_stats**2 + dist2/dist2_stats**2)/ (1.0/dist1_stats**2+1.0/dist2_stats**2)
        if bg1 == bg2:
            bg = bg1
            bg_err = np.sqrt(bg)
        else:
            logging.warning("bg1({0}) and bg2({2}) don't match".format(bg1,bg2))
        if n50_1 == n50_2:    
            n50 = n50_1
            n50_err = np.sqrt(n50) #assume Gaussian counting statistics
        else:
            logging.warning("n50_1({0}) and n50_2({1}) don't match".format(n50_1,n50_2))
        if N50_1 == N50_2:
            N50 = N50_1
            N50_err = np.sqrt(N50)
            #logging.info("{0} N50: {1}".format(self.name,N50))
        else:
            logging.warning("N50_1({0}) and N50_2({1}) don't match".format(N50_1,N50_2))
        #logging.info("{0} background(/ms): {1}, n50(uncorrected): {2}, N50(uncorrected): {3}, n100_150(uncorrected): {4}, N100_150(corrected): {5}".format(data["detector_name"],bg,n50,N50,n100_150,N100_150))
        N100_150_err = np.sqrt(N100_150)
        n100_150_err = np.sqrt(n100_150) # assume Gaussian counting statistics
        
        #calculate mdist_stats (simplify using variables: v1, v2, ...)
        v1 = (-1*(N100_150-b*N50)**(0.5)*N50**(-2)-0.5*b*N50**(-1)*(N100_150-b*N50)**(-0.5))
        v2 = (0.5*(N100_150-b*N50)**(-0.5)*N50**(-1))
        v3 = ((v1*N50_err)**2+(v2*N100_150_err)**2)**(-1)
        G = -5*imf**(0.5)*N50**(-1.5) #diff dist1 wrt N50
        E = 10*m**(-0.5)*v1 #diff dist2 wrt N50
        F = 10*m**(-0.5)*v2 #diff dist2 wrt N100_150
        A = 0.12*imf**(-1)*(N50/N50_err)**2 #diff (dist1_stats)**(-2) wrt N50
        #diff (dist2_stats)**(-2) wrt N50
        C = -0.01*m*v3**2*(N50_err**2*2*v1*(2*(N100_150-b*N50)**(0.5)*N50**(-3)+0.5*b*N50**(-2)*(N100_150-b*N50)**(-0.5)+0.5*b*(N100_150-b*N50)**(-0.5)*N50**(-2)-0.25*b**2*N50**(-1)*(N100_150-b*N50)**(-1.5)) + N100_150_err**2*2*v2*(-0.5*(N100_150-b*N50)**(-0.5)*N50**(-2)+0.25*b*(N100_150-b*N50)**(-1.5)*N50**(-1)))
        #diff (dist2_stats)**(-2) wrt N100_150
        D = -0.01*m*v3**2*(N50_err**2*2*v1*(-0.5*(N100_150-b*N50)**(-0.5)*N50**(-2)+0.25*b*(N100_150-b*N50)**(-1.5)*N50**(-1)) + N100_150_err**2*2*v2*(-0.25)*(N100_150-b*N50)**(-1.5)*N50**(-1))
        s1 = dist1_stats**(-2)
        s2 = dist2_stats**(-2)
        #diff mdist wrt N50 or n50(uncorrected)
        d1 = ((G*s1+dist1*A+E*s2+dist2*C)*(s1+s2)**(-1) - (dist1*s1+dist2*s2)*(s1+s2)**(-2)*(A+C))
        #diff mdist wty N100_150 or n100_150(uncorrected)
        d2 = ((F*s2+dist2*D)*(s1+s2)**(-1) - (dist1*s1+dist2*s2)*(s1+s2)**(-2)*D)
        #diff mdist wrt bg
        d3 = -(d1+d2)
        #term associated with n50
        t1 = n50_err*d1
        #term assiciated with n100_150
        t2 = n100_150_err*d2
        #term associated with bg
        t3 = bg_err*d3
        mdist_stats = np.sqrt(t1**2 + t2**2 + t3**2)

        mdist_sys = 1.0/np.sqrt(1.0/dist1_sys**2+1.0/dist2_sys**2)
        mdist_err = np.sqrt(mdist_stats**2+mdist_sys**2)

        return (mdist, mdist_err, mdist_stats, mdist_sys, bg, dist1, dist1_err, dist1_stats, dist1_sys, bg1, dist2, dist2_err, dist2_stats, dist2_sys, bg2, n50, N50, n100_150, N100_150)               
    
    def alert(self, data):
        (mdist, mdist_err, mdist_stats, mdist_sys, bg, dist1, dist1_err, dist1_stats, dist1_sys, bg1, dist2, dist2_err, dist2_stats, dist2_sys, bg2, n50, N50, n100_150, N100_150) = self.mean_dist(data)
        d = { self.out_field: mdist, self.out_field+"_err": mdist_err, self.out_field+"_stats": mdist_stats, self.out_field+"_sys": mdist_sys, \
            "dist1": dist1, "dist1_err": dist1_err, "dist1_stats": dist1_stats, "dist1_sys": dist1_stats, \
            "dist2": dist2, "dist2_err": dist2_err, "dist2_stats": dist2_stats, "dist2_sys": dist2_stats, \
            "background": bg, "n50": n50, "N50": N50, "n100_150": n100_150, "N100_150": N100_150
        }
        data.update(d)
        return True
