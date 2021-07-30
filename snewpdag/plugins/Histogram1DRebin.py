"""
Plugin to re-bin a 1D histogram
Only combines integer numbers of bins

Configuration options:
    factor: number of old bins per new bin; eg. factor=5 would rebin a 100-bin hist to 20 bins

Input data:
    - Reponds only to 'report'
    - Rewrites nbins; bins in the data

"""

import numpy as np
import logging

from snewpdag.dag import Node


class Histogram1DRebin(Node):
    def __init__(self, factor, **kwargs):
        self.factor = factor
        super().__init__(**kwargs)

    def report(self, data):
        old_nbins = data['nbins']
        if (old_nbins % self.factor) != 0:
            print("ERROR: factor does not divide nbins")
            return False

        new_nbins = old_nbins // self.factor
        new_bins = np.empty(new_nbins, 'float64')

        print("Rebinning {}->{} bins".format(old_nbins, new_nbins))

        for i_new_bin in range(new_nbins):
            new_bin_value = np.sum(data['bins'][i_new_bin * self.factor : (i_new_bin + 1) * self.factor])
            new_bins[i_new_bin] = new_bin_value

        data['nbins'] = new_nbins
        data['bins'] = new_bins

        return True

"""

Qs:
    - When should I be returning false/true?
    - Is it alright just to OVERWRITE data like that?


"""
