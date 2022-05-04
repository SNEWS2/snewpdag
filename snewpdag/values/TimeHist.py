"""
TimeHist - time histogram of events
"""
import logging
import numpy as np
from snewpdag.dag.lib import normalize_time, subtract_time

class TimeHist:
  def __init__(self, start_time, start_ns, time_span_s, nbins=0, data=[]):
    self.start = np.array([start_time, start_ns])
    self.time_span_s = time_span_s
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
    i = np.array([index]) if np.isscalar(index) else np.array(index)
    t0 = np.full((len(index), 2), self.start)
    dt = i * time_span_s / self.nbins()
    t1 = t0 + dt
    return normalize_time(t1)

