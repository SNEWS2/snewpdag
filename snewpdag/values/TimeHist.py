"""
TimeHist - time histogram of events

Data is stored (and can be manipulated) in self.data.
"""
import logging
import numpy as np
from snewpdag.dag.lib import time_tuple_from_float, normalize_time, subtract_time, ns_per_second

class TimeHist:
  def __init__(self, start, time_span, nbins=0, data=[]):
    """
    start_time:  float or (s,ns)
    time_span:  duration of histogram in seconds
    nbins (optional):  number of bins
    data (optional):  bin data
    if nbins not specified, nbins set to length of data.
    if data has more than nbins elements, it's truncated to nbins.
    """
    self.start = time_tuple_from_float(start) if np.isscalar(start) else np.array(start)
    self.time_span = time_span
    if nbins == 0:
      self.bins = np.array(data)
    else:
      if len(data) > 0:
        self.bins = np.array(data[:nbins])
      else:
        self.bins = np.zeros(nbins)

  def nbins(self):
    return len(self.bins)

  def bin_start(self, index):
    """
    Return start time of bin number.
    """
    dt = self.time_span / len(self.bins)
    t1 = self.start[1] + index * ns_per_second * dt
    return normalize_time((self.start[0], t1))

