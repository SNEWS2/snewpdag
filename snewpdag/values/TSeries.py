"""
TSeries - a series of event times

Internal storage:
  reference is in absolute ns from Unix epoch (int64).
  start, stop, and offsets are in ns from reference.
  Note that offsets aren't automatically sorted.  Call sort() to do so.
"""
import logging
import numbers
import numpy as np
from astropy.time import Time
from astropy import units as u
from snewpdag.dag.lib import field2ns, t2ns, ns_per_second

class TSeries:
  def __init__(self, reference, unit=None, **kwargs):
    """
    Arguments:
      reference = reference time
      unit = unit to use for reference, start, and stop times. Default u.ns.
      start (optional) = starting time
      stop (optional) = stopping time
    Times can come in the following formats:
      string - a time string
      number - assumed to be seconds since Unix epoch
      Quantity - assumed to be time-like, since Unix epoch
    """
    uu = u.ns if unit == None else unit
    self.reference = field2ns(reference, unit=uu)
    self.has_start = ('start' in kwargs)
    if self.has_start:
      self.start = field2ns(kwargs['start'], unit=uu) - self.reference
    self.has_stop = ('stop' in kwargs)
    if self.has_stop:
      self.stop = field2ns(kwargs['stop'], unit=uu) - self.reference
    self.offsets = np.array([], dtype=np.int64)

  def to_dict(self):
    d = { 'reference': self.reference, 'offsets': self.offsets.copy() }
    if self.has_start:
      d['start'] = self.start
    if self.has_stop:
      d['stop'] = self.stop
    return d

  def sort(self):
    self.offsets.sort()

  def add_offsets(self, offsets, unit=None):
    """
    offsets = an array of offsets from the reference time.
      If type is simple numeric, assume it's s from reference.
      If type is Quantity, convert to appropriate unit.
    unit = unit override (default u.s)
    """
    dt = t2ns(offsets, unit=unit)
    if self.has_start or self.has_stop:
      m = (dt >= self.start) if self.has_start else np.full_like(dt, True)
      if self.has_stop:
        m &= (dt < self.stop)
      self.offsets = np.append(self.offsets, dt[m])
    else:
      self.offsets = np.append(self.offsets, dt)

  def add_times(self, times, unit=None):
    """
    times = an array of numeric times.
      If type is simple numeric, assume it's s from epoch.
      If type is Quantity, assume it's time from epoch.
    unit = unit override (default u.s)
    """
    dt = t2ns(times, unit=unit) - self.reference
    self.add_offsets(dt, unit=u.ns)

  def event(self, index):
    """
    get the time of the index event(s), in ns since epoch.
    if index is a simple number, just return one result.
    if index is an array of indices, return corresponding results in array.
    """
    try:
      return self.offsets[index] + self.reference
    except IndexError:
      logging.error('TSeries: index out of bounds')
      return None

  def histogram(self, nbins, start=None, stop=None):
    """
    Make a histogram out of the time series.
    """
    if start != None:
      t0 = field2ns(start)
    elif self.has_start:
      t0 = self.start
    else:
      t0 = np.min(self.offsets)
    if stop != None:
      t1 = field2ns(stop)
    elif self.has_stop:
      t1 = self.stop
    else:
      span = np.max(self.offsets) - t0
      width = 1.01 * span # 1% beyond latest time
      t1 = t0 + width
    logging.debug('TSeries.histogram: t0={}, t1={}'.format(t0, t1))
    h, edges = np.histogram(self.offsets, bins=nbins, range=(t0, t1))
    return h

  def integral(self, **kwargs):
    """
    Count the events between the start and stop times if given.
    """
    f0 = 'start' in kwargs
    f1 = 'stop' in kwargs
    if f0 or f1:
      m = np.full_like(self.offsets, True)
      if f0:
        t0 = field2ns(kwargs['start']) - self.reference
        m &= self.offsets >= t0
      if f1:
        t1 = field2ns(kwargs['stop']) - self.reference
        m &= self.offsets < t1
      return np.sum(m)
    else:
      return self.offsets.size

