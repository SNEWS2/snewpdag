"""
TimeHist - time histogram of events

Data is stored (and can be manipulated) in self.data.
"""
import logging
import numpy as np
from snewpdag.values import Hist1D
from snewpdag.dag.lib import time_tuple_from_float, normalize_time, subtract_time, ns_per_second

class TimeHist(Hist1D):
  def __init__(self, start, time_span, nbins=0, data=[]):
    """
    start_time:  float or (s,ns)
    time_span:  duration of histogram in seconds
    nbins (optional):  number of bins
    data (optional):  bin data
    if nbins not specified, nbins set to length of data.
    if data has more than nbins elements, it's truncated to nbins.
    Low edge of histogram is rendered as 0, so x-axis is time offset.
    """
    self.start = time_tuple_from_float(start) if np.isscalar(start) else np.array(start)
    self.time_span = time_span
    nb = max(nbins, len(data)) if nbins == 0 or len(data) == 0 else \
         min(nbins, len(data))
    if nb == 0:
      logging.error("TimeHist: zero-length histogram created")
    super().__init__(nb, 0.0, self.time_span)
    if len(data) > 0:
      self.bins = np.array(data[:nb])

  def bin_start(self, index):
    """
    Return start time of bin number.
    """
    dt = self.time_span / len(self.bins)
    t1 = self.start[1] + index * ns_per_second * dt
    return normalize_time((self.start[0], t1))

  def add_offsets(self, offsets):
    """
    offsets:  an array of ns offsets from start time
    """
    self.fill(np.array(offsets) / ns_per_second)

  def add_times(self, times):
    """
    times:  an array of (s,ns) times.  Subtract start time before storing.
    """
    if np.shape(times)[-1] < 2:
      logging.error("input array has wrong shape {}".format(np.shape(times)))
      return
    d = subtract_time(times, self.start)
    t = np.multiply(d[...,0], ns_per_second, dtype=np.int64)
    t = np.add(t, d[...,1], dtype=np.int64)
    self.add_offsets(t)

