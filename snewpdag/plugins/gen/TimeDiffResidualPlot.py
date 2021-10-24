"""
TimeDiffResidualPlot: Plot the time difference residual of each detector pair

Output: histogram plot of the time difference residual of each detector pair
"""


import logging
import numpy as np
import itertools
import matplotlib.pyplot as plt 
from snewpdag.dag import lib
from snewpdag.dag import Node
from snewpdag.plugins.gen.TimeOffset import TimeOffset

class TimeDiffResidualPlot(Node):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    #Calculate the time difference of every detector pair in a given dictionary while checking they are all within 40ms. 
    #Input c is either data['gen']['sn_times'] or data['gen']['neutrino_times']
    def time_diff_max(self, c):
        tm = [0, 40000000]
        l = {}
        for detpair in itertools.combinations(c, 2):
            if detpair[0] == "Earth":
                continue
            a = c[detpair[0]]
            b = c[detpair[1]]
            d = lib.subtract_time(a,b)
            if d[0] != 0 or abs(d[1]) > tm[1]:
                logging.warning('Time difference exceeds 40ms for detector pair {}'.format(detpair))
            l[detpair] = tuple(d)
        return l
    
    #Plot the time residual between true and expected time differnce of each detector pair in a histogram,
    #the true time difference of each detector is plotted as a red line
    def time_residual_hist(self, data):
        a = self.time_diff_max(data['gen']['sn_times'])
        d = {}
        file = 'detector_location.csv'
        mc_trial = 1000
        for i in range(mc_trial):
            m = TimeOffset(file)
            m.alert(data)
            b = self.time_diff_max(data['gen']['neutrino_times'])
            for pair in a:
                c_tuple = lib.subtract_time(b[pair], a[pair])
                c = c_tuple[0]*int(1e9) + c_tuple[1]
                if pair in d:
                    d[pair].append(c)
                else:
                    d[pair] = [c,]
                    
        for pair in a:
            bins = 10
            plt.figure()
            plt.hist(d[pair], bins = bins)
            b1 = m.detector_offset[pair[0]][1]
            b2 = m.detector_offset[pair[1]][1]
            diff_b = (b1-b2)*1e9 
            y,bin_edges = np.histogram(d[pair],bins=bins)
            bin_centers = 0.5*(bin_edges[1:] + bin_edges[:-1])
            poisson_error = np.sqrt(y)
            
            plt.vlines(diff_b, 0, max(y), 'r')
            plt.xlabel("Time difference residual of {} (ns)".format(pair))
            plt.ylabel("Count")
            plt.bar(bin_centers, y, yerr=poisson_error, capsize = 2)
            plt.show()
            plt.savefig("Time Difference Residual Histogram {}.png".format(pair))
