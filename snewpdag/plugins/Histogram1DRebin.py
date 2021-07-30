"""
Plugin to re-bin a 1D histogram, combining integer numbers of bins.
This plugin should listen to a Histogram1D; can be listened-to by eg. a Histogram1D renderer

Configuration options:
    factor: number of old bins per new bin; eg. factor=5 would rebin a 100-bin hist to 20 bins.
        If factor does not divide nbins, the upper x limit is reduced and excess counts are added to the overflow.

Input data:
    action: report or alert
    Histogram dictionary as produced by Histogram1D; namely must contain
    - xlow, xhigh; x-axis limits
    - nbins; number of bins
    - bins; array of bin counts
    - overflow
"""

import numpy as np
import logging

from snewpdag.dag import Node


class Histogram1DRebin(Node):

    def __init__(self, factor, **kwargs):
        self.factor = factor
        super().__init__(**kwargs)

    def report(self, data):
        if not ("xlow" in data and "xhigh" in data and "nbins" in data and "bins" in data and "overflow" in data):
            logging.error("Histogram1DRebin has not been supplied with a valid histogram")
            return False

        old_nbins = data['nbins']
        old_bin_width = (data['xhigh'] - data['xlow']) / old_nbins

        new_nbins = old_nbins // self.factor
        new_bins = np.empty(new_nbins, 'float64')

        logging.info("Rebinning {}->{} bins".format(old_nbins, new_nbins))

        for i_new_bin in range(new_nbins):
            new_bin_value = np.sum(data['bins'][i_new_bin * self.factor : (i_new_bin + 1) * self.factor])
            new_bins[i_new_bin] = new_bin_value

        # Add everything else to the overflow bin and change the top limit...
        data['overflow'] += np.sum(data['bins'][new_nbins * self.factor:])
        data['xhigh'] = data['xlow'] + old_bin_width * (old_nbins // self.factor) * self.factor

        # Update n_bins and bins in the payload
        data['nbins'] = new_nbins
        data['bins'] = new_bins

        return True

    def alert(self, data):
        return self.report(data)
