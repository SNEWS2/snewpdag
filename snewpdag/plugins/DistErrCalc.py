'''
This plugin calculates the rmse and relative error of mdist

Constructor arguments:
    xlow: low edge of true dist 
    xhigh: high edge of true dist
    xno: no of true dist (might modify to obtain from payload, now set to (4,40,100) to match MeanDist.py)
    
Output json:
    alert:  no output
    reset:  no output
    revoke:  no output
    report:  add the following
                rel_err: relative error

'''

import logging
import numpy as np
from snewpdag.dag import Node

class DistErrCalc(Node):
    def __init__(self, xlow, xhigh, xno, **kwargs):
        self.xlow = xlow#4
        self.xhigh = xhigh#40
        self.xno = xno#100
        self.true_dist = np.linspace(self.xlow, self.xhigh, self.xno, endpoint=True)
        super().__init__(**kwargs)
        self.clear()

    def clear(self):
        self.sum = np.zeros(self.xno)
        self.sum2 = np.zeros(self.xno)
        #self.err2 = np.zeros(self.xno)
        self.exp_err2 = np.zeros(self.xno)
        self.changed = True
        
    def fill(self,data):
        mdist = data["mdist"]
        mdist_err = data["mdist_err"]
        self.sum += mdist
        self.sum2 += mdist**2
        #self.err2 += (mdist-self.true_dist)**2
        self.exp_err2 += mdist_err**2
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
            std = np.sqrt(self.sum2/1000 - (self.sum/1000)**2)
            rel_err = (std/self.true_dist)*100
            exp_rmse = np.sqrt(self.exp_err2/1000)
            exp_rel_err = (exp_rmse/self.true_dist)*100
            d = {"rel_err": rel_err, "exp_rel_err": exp_rel_err}
            data.update(d)
            self.changed = False
            return True
        else:
            return False # or else will duplicate same plot for same report
