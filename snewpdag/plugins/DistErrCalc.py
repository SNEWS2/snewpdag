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
        self.err2 = np.zeros(self.xno)
        self.changed = True
        
    def fill(self,data):
        mdist = data["mdist"]
        mdis_err = data["mdist_err"]
        self.err2 += (mdist-self.true_dist)**2
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
            rmse = np.sqrt(self.err2/self.xno)
            rel_err = np.absolute(rmse/self.true_dist)*100
            d = {"rel_err": rel_err}
            data.update(d)
            self.changed = False
            return True
        else:
            return False # or else will duplicate same plot for same report
