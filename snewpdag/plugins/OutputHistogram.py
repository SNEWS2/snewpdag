'''
This plugin receives an array as the payload.
The array contains the frequency for each bin.
A plot (containing one or more histograms) is generated via the data.

Constructor arguments:
    nbins: number of bins
    xlow: low edge of histogram
    xhigh: high edge of histogram

Output:
    Histogram in PNG form
'''

import numpy as np
import matplotlib.pyplot as plt

from snewpdag.dag import Node

class OutputHistogram(Node):
    def __init__(self, nbins, xlow, xhigh, **kwargs):
        self.nbins = nbins
        self.xlow = xlow
        self.xhigh = xhigh
        self.index = kwargs.pop('index', None)
        super().__init__(**kwargs)

    def plot_histogram(self, data_freq):
        data = []
        labels = []
        bin_size = (self.xhigh - self.xlow) / self.nbins
        if self.index != None:
            for j in range(0,self.index+1):
                temp = []
                for i in range(0, self.nbins):      # e.g.  express data_freq [ 0, 1, 1, 0, 1, 0, 0, 0, 0, 0 ]
                    bin = self.xlow + i*bin_size    #       as [0.1, 0.3, 0.7] with xlow = -0.9 & bin_size = 0.2
                    while data_freq[j][i] != 0:
                        temp.append(bin)
                        data_freq[j][i] -= 1
                data.append(temp)
                labels.append(j)

            plt.hist(data, density=False, bins=self.nbins, label=labels)
            plt.legend(loc='upper right')
            
        else:
            for i in range(0, self.nbins):      # e.g.  express data_freq [ 0, 1, 1, 0, 1, 0, 0, 0, 0, 0 ]
                bin = self.xlow + i*bin_size    #       as [0.1, 0.3, 0.7] with xlow = -0.9 & bin_size = 0.2
                while data_freq[i] != 0:
                    data.append(bin)
                    data_freq[i] -= 1
            
            plt.hist(data, density=False, bins=self.nbins)

        plt.ylabel('Count number')
        plt.xlabel('Data')
        plt.savefig(self.name + '.png')
        plt.clf() # this line is needed such that the data won't seep through multiple unit tests
        return