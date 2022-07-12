"""
TimeHist - time histogram of events

Data is stored (and can be manipulated) in self.data.
"""
import logging
import numpy as np
from snewpdag.values import Hist1D
from snewpdag.dag.lib import time_tuple_from_float, normalize_time, subtract_time, ns_per_second

class TimeHist(Hist1D):
  def __init__(self, start, duration, nbins=100, data=[]):
    """
    start_time:  float or (s,ns)
    duration:  duration of histogram in seconds
    nbins (optional):  number of bins if no data array, default 100
    data (optional):  bin data

    if data is not specified, nbins will be set to argument (or its default).
    length of data array supersedes nbins argument.
    Low edge of histogram is rendered as 0, so x-axis is time offset.
    """
    self.start = time_tuple_from_float(start) if np.isscalar(start) else np.array(start)
    self.duration = duration
    nb = nbins if len(data) == 0 else len(data)
    super().__init__(nb, 0.0, self.duration)
    if len(data) > 0:
      self.bins = np.array(data)

  def bin_start(self, index):
    """
    Return start time of bin number.
    """
    dt = self.duration / len(self.bins)
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

