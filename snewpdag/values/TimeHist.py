"""
TimeHist - time histogram of events

Data is stored (and can be manipulated) in self.data.
"""
import logging
import numpy as np
from snewpdag.values import Hist1D
from snewpdag.dag.lib import time_tuple_from_field, normalize_time, subtract_time, offset_from_time_tuple, ns_per_second

class TimeHist(Hist1D):
  def __init__(self, start, duration, nbins=100, data=[], **kwargs):
    """
    start:  float or (s,ns)
    duration:  duration of histogram in seconds
    reference (optional):  float or (s,ns). Defines t=0.
      Default is the same as start_time.
    nbins (optional):  number of bins if no data array, default 100
    data (optional):  bin data

    if data is not specified, nbins will be set to argument (or its default).
    length of data array supersedes nbins argument.
    Low edge of histogram is rendered as 0, so x-axis is time offset.
    """
    self.start = time_tuple_from_field(start)
    reft = kwargs.pop('reference', start)
    logging.debug('TimeHist: fields start = {}, reference = {}'.format(start, reft))
    self.reference = time_tuple_from_field(reft)
    logging.debug('TimeHist: start = {}, reference = {}'.format(self.start, self.reference))
    tlow = offset_from_time_tuple(subtract_time( \
           self.start, self.reference)) / ns_per_second
    self.duration = duration
    nb = nbins if len(data) == 0 else len(data)
    super().__init__(nb, tlow, self.duration)
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
    a = np.array([offsets]) if np.shape(offsets) == () else np.array(offsets)
    self.fill(a / ns_per_second)

  def add_offsets_s(self, offsets):
    """
    offsets:  an array of offsets (in seconds) from start time
    """
    self.fill(np.array(offsets))

  def add_offsets_ms(self, offsets):
    """
    offsets:  an array of offsets (in ms) from start time
    """
    self.fill(np.array(offsets) / 1000.0)

  def add_times(self, times):
    """
    times:  an array of times.  Subtract start time before storing.
      s        a single time (float)
      [s1,s2]  two times (floats)
      (s,ns)   a single (s,ns) - specifically needs to be a tuple!
      [(s1,ns1),(s2,ns2)]  two times (s,ns)
    """
    ts = np.array(times)
    shape = np.shape(ts)
    if (len(shape) == 2 and shape[1] == 2) or \
        (shape == (2,) and isinstance(times, tuple)):
      # array of (s,ns)
      d = subtract_time(times, self.start)
      t = np.multiply(d[...,0], ns_per_second, dtype=np.int64)
      t = np.add(t, d[...,1], dtype=np.int64)
      self.add_offsets(t)
    elif shape == () or len(shape) == 1:
      # array or scalar of s in float
      # (note (s,ns) as a tuple already handled in previous section)
      t0 = self.start[0] + self.start[1] / ns_per_second
      t = ts - t0
      self.add_offsets_s(t)
    else:
      logging.error("input array has wrong shape {}".format(shape))
      return

