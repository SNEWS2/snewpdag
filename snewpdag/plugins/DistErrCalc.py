'''
DistErrCalc: calculates the relative errors of distance estimate (data and expectation) as well as the covariance matrix of dist1 and dist2

Constructor arguments:
    in_field: string, name of field containing weighted mean dist
                to match "out_field" of MeanDist
    xno: no. of true dist
    
Output json:
    alert:  no output
    reset:  no output
    revoke:  no output
    report:  add the following
                rel_err: relative error
                exp_rel_err: expected relative combined error
                exp_rel_stats: expected relative statistical error
                exp_rel_sys: expected relative systematic error

'''

import logging
import numpy as np
from snewpdag.dag import Node

class DistErrCalc(Node):
    def __init__(self, in_field, xno, **kwargs):
        self.in_field = in_field
        self.xno = xno
        super().__init__(**kwargs)
        self.clear()

    def clear(self):
        self.sum = np.zeros(self.xno)
        self.sum2 = np.zeros(self.xno)
        self.exp_err2 = np.zeros(self.xno)
        self.exp_stats2 = np.zeros(self.xno)
        self.exp_sys2 = np.zeros(self.xno)
        self.dist_count = np.zeros(self.xno)
        self.changed = True
        #for calculating cov matrix
        self.dist1_dict = {}
        self.dist2_dict = {}

    def fill(self,data):
        d_lo = data["d_lo"]
        d_hi = data["d_hi"]
        d_no = data["d_no"]
        true_dist = data["sn_distance"]
        #logging.info('true_dist:{}'.format(true_dist))
        spacing = (d_hi-d_lo) / (d_no-1) 
        index = int((true_dist-d_lo) / spacing) #index of the sn_distance in dist_list
        #logging.info('index:{}'.format((true_dist-d_lo) / spacing))

        dist = data[self.in_field]
        self.sum[index] += dist
        self.sum2[index] += dist**2

        dist_err = data[self.in_field+"_err"]
        self.exp_err2[index] += dist_err**2

        dist_stats = data[self.in_field+"_stats"]
        self.exp_stats2[index] += dist_stats**2

        dist_sys = data[self.in_field+"_sys"]
        self.exp_sys2[index] += dist_sys**2
        #count the number of times a true distance is used
        self.dist_count[index]+=1
        self.changed = True

        #for calculating cov matrix
        dist1 = data["dist1"]
        if true_dist in self.dist1_dict:
            self.dist1_dict[true_dist].append(dist1)
        else:
            self.dist1_dict[true_dist] = [dist1]
        dist2 = data["dist2"]
        if true_dist in self.dist2_dict:
            self.dist2_dict[true_dist].append(dist2)
        else:
            self.dist2_dict[true_dist] = [dist2]

    def alert(self, data):
        self.fill(data)
        return False # don't forward an alert

    def reset(self, data):
        return False

    def revoke(self, data):
        return False

    def report(self, data):
        if self.changed:
            true_dist = np.linspace(data["d_lo"], data["d_hi"], data["d_no"], endpoint=True)
            #calculate covariance matrix
            C = {}
            for i in true_dist:
                C[i] = np.cov(self.dist1_dict[i], self.dist2_dict[i])

            #logging.info('Covariance matrix:{}'.format(C))
            
            #calculate errors
            std = np.sqrt(self.sum2/self.dist_count - (self.sum/self.dist_count)**2)
            rel_err = (std/true_dist)*100
                #exp_rmse = np.sqrt(self.exp_err2/self.dist_count)
                #exp_rel_err = (exp_rmse/self.true_dist)*100

            exp_rmse_stats = np.sqrt(self.exp_stats2/self.dist_count)
            exp_rel_stats = (exp_rmse_stats/true_dist)*100

            exp_rmse_sys = np.sqrt(self.exp_sys2/self.dist_count)
            exp_rel_sys = (exp_rmse_sys/true_dist)*100      
                
            exp_rmse = np.sqrt(exp_rmse_stats**2+exp_rmse_sys**2)
            exp_rel_err = (exp_rmse/true_dist)*100
            d = {"rel_err": rel_err, "exp_rel_err": exp_rel_err, "exp_rel_stats": exp_rel_stats, "exp_rel_sys": exp_rel_sys}
            data.update(d)
            self.changed = False
            
            return True
        else:
            return False # or else will duplicate same plot for same report
