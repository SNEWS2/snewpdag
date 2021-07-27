'''
This plugin render plots of relative error of mdist against true dist

Constructor arguments:
    xlow: low edge of true dist 
    xhigh: high edge of true dist
    xno: no of true dist (might modify to obtain from payload, now set to (4,40,100) to match MeanDist.py)
    title:  plot title (top of plot)
    xlabel:  x axis label
    ylabel:  y axis label
    filename:  output filename, with fields
                {0} renderer name

Input data:
    action: only respond to 'report'
    rel_err: relative error of mdist
    
"""

'''

import matplotlib.pyplot as plt
import numpy as np
from snewpdag.dag import Node

class DistErrPlot(Node):
    def __init__(self, title, xlabel, ylabel, filename, **kwargs):
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.filename = filename # include pattern to include index
        self.xlow = 4#xlow
        self.xhigh = 40#xhigh
        self.xno = 100#xno
        self.true_dist = np.linspace(self.xlow, self.xhigh, self.xno, endpoint=True)
        super().__init__(**kwargs)

    def render(self, rel_err, exp_rel_err):
        fig, ax = plt.subplots()
        ax.plot(self.true_dist, rel_err, label="Data")
        ax.plot(self.true_dist, exp_rel_err, label="Expected")
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.set_title('{0}'.format(self.title))
        ax.legend()
        fig.tight_layout()
        fname = self.filename.format(self.name, 0, 0)
        plt.savefig(fname)

    def report(self, data):
        rel_err = data["rel_err"]
        exp_rel_err = data["exp_rel_err"]
        self.render(rel_err, exp_rel_err)
        return True
