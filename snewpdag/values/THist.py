"""
THist - a time histogram of events

Histogram range is from (start-ref) to (stop-ref), in seconds.
"""
import logging
import numbers
import numpy as np
from astropy.time import Time
from astropy import units as u
from snewpdag.values import Hist1D
from snewpdag.dag.lib import field2ns, t2ns, ns_per_second

class THist(Hist1D):
  def __init__(self, reference, nbins, start, stop):
    self.reference = field2ns(reference) # ns
    self.nbins = nbins
    self.start = field2ns(start) - self.reference # ns
    self.stop = field2ns(stop) - self.reference # ns
    t0 = (self.start * u.ns).to(u.s)
    t1 = (self.stop * u.ns).to(u.s)
    super().__init__(self.nbins, t0.value, t1.value) # s

  def to_dict(self):
    d = { 'reference': self.reference, #ns
          'start': self.start, #ns
          'stop': self.stop, #ns
          'nbins': self.nbins,
          'hist': super().to_dict()
        }
    return d

  def bin_start(self, index):
    """
    Returns the start time in ns since Unix epoch
    """
    dt = (self.stop - self.start) / self.nbins
    return index * dt + self.start + self.reference

  def add_offsets(self, offsets, unit=None):
    """
    offsets = an array of offsets from the reference time.
      If type is simple numeric, assume it's s from reference.
      If type is Quantity, convert to appropriate unit.
    """
    dt = t2ns(offsets, unit=unit) / ns_per_second
    self.fill(dt)
  
  def add_times(self, times, unit=None):
    """
    times = an array of numeric times.
      If type is simple numeric, assume it's s from epoch.
      If type is Quantity, assume it's time from epoch.
    """
    dt = (t2ns(times, unit=unit) - self.reference) / ns_per_second
    self.fill(dt)

  def histogram(self, nbins, start=None, stop=None):
    """
    Rebin.  Slow plodding method.  Can be made faster.
    If new bins don't align with old, uses closest bin edges.
    """
    t0 = self.tlow if start == None \
         else (field2ns(start) - self.reference) / ns_per_second
    t1 = self.thigh if stop == None \
         else (field2ns(stop) - self.reference) / ns_per_second
    js = self.bin(np.linspace(t0, t1, num=nbins, endpoint=False))
    m = (js >= 0) & (js < self.nbins)
    ks = js[m]
    h = np.zeros(nbins)
    for i in range(len(ks)):
      h[ks[i]] += self.bins[i]
    return h

  def integral(self, **kwargs):
    """
    Count events in bins between start and stop times if given.
    Gives best approximation based on closest bin edges.
    """
    f0 = 'start' in kwargs
    f1 = 'stop' in kwargs
    if f0 or f1:
      if f0:
        t0 = (field2ns(kwargs['start']) - self.reference) / ns_per_second
        i0 = np.round((t0 - self.xlow) * self.nbins / self.xwidth)
      else:
        i0 = 0
      if f1:
        t1 = (field2ns(kwargs['stop']) - self.reference) / ns_per_second
        i1 = np.round((t1 - self.xlow) * self.nbins / self.xwidth)
      else:
        i1 = self.nbins
      return np.sum(self.bins[i0:i1])
    else:
      return np.sum(self.bins)

