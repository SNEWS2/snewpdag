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
        self.exp_mdist_stats2 = np.zeros(self.xno)
        self.dist_count = np.zeros(self.xno)
        self.changed = True
        self.exp_dist1_stats2 = np.zeros(self.xno)
        self.exp_dist2_stats2 = np.zeros(self.xno)

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

        dist_stats = data[self.in_field+"_stats"]
        self.exp_mdist_stats2[index] += dist_stats**2
        dist1_stats = data["dist1_stats"]
        self.exp_dist1_stats2[index] += dist1_stats**2
        dist2_stats = data["dist2_stats"]
        self.exp_dist2_stats2[index] += dist2_stats**2

        #count the number of times a true distance is used
        self.dist_count[index]+=1
        self.changed = True


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
            
            #calculate errors
            std = np.sqrt(self.sum2/self.dist_count - (self.sum/self.dist_count)**2)
            rel_err = (std/true_dist)*100

            exp_rmse_mdist_stats = np.sqrt(self.exp_mdist_stats2/self.dist_count)
            exp_rel_mdist_stats = (exp_rmse_mdist_stats/true_dist)*100

            exp_rmse_dist1_stats = np.sqrt(self.exp_dist1_stats2/self.dist_count)
            exp_rel_dist1_stats = (exp_rmse_dist1_stats/true_dist)*100      
                
            exp_rmse_dist2_stats = np.sqrt(self.exp_dist2_stats2/self.dist_count)
            exp_rel_dist2_stats = (exp_rmse_dist2_stats/true_dist)*100 
            d = {"rel_err": rel_err, "exp_rel_dist1_stats": exp_rel_dist1_stats, "exp_rel_dist2_stats": exp_rel_dist2_stats, "exp_rel_mdist_stats": exp_rel_mdist_stats}
            data.update(d)
            logging.info("{0} dist_count:{1}".format(self.name,self.dist_count))
            self.changed = False
            
            return True
        else:
            return False # or else will duplicate same plot for same report
