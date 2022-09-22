"""
TimeSeries - a series of events

Timestamps are simply seconds into a SNEWS or snewpdag instance epoch,
represented as floats which can be negative as well as positive.
"""
import logging
import numpy as np

class TimeSeries:
  def __init__(self, start=None, stop=None):
    """
    start:  start time (float), or None if no minimum time
    stop:  stop time (float), or None if no maximum time
    """
    self.start = start
    self.stop = stop
    self.times = np.array([], dtype=np.float64)

  def to_dict(self):
    return { 'start': self.start, 'stop': self.stop,
             'times': [ t for t in self.times ],
           }

  def sort(self):
    """
    Sort the times
    """
    self.times.sort()

  def add(self, times):
    """
    Add times to series.
    times:  an array of timestamps, assumed to be seconds unless
            it's an array of Quantity, in which case convert to seconds.
    """
    ts = times.to(u.s) if hasattr(times, 'unit') else times
    if self.start == self.stop: # also includes both being None
      self.times = np.append(self.times, ts)
    else:
      m = np.full_like(ts, True) if self.start == None else (ts >= self.start)
      if self.stop != None:
        m &= (ts < self.stop)
      self.times = np.append(self.times, ts[m])

  def histogram(self, nbins, start=None, stop=None):
    """
    Make a histogram out of the time series.
    """
    t0 = self.start if start == None else start
    t1 = self.stop if stop == None else stop
    if t0 == None:
      if t1 == None: # no limits, so let np.histogram optimize
        h, edges = np.histogram(self.times, bins=nbins)
      else: # only upper limit
        h, edges = np.histogram(self.times[self.times < t1], bins=nbins)
    else:
      if t1 == None: # only lower limit
        h, edges = np.histogram(self.times[self.times >= t0], bins=nbins)
      else: # both limits
        h, edges = np.histogram(self.times, bins=nbins, range=(t0, t1))
    return h, edges

  def integral(self, start=None, stop=None):
    """
    Count the events between the start and stop times.
    By default this returns the total number of events.
    """
    t0 = self.start if start == None else start
    t1 = self.stop if stop == None else stop
    if t0 == None:
      if t1 == None: # no limits
        return np.times.size
      else: # only upper limit
        return np.sum(self.times < t1)
    else:
      if t1 == None: # only lower limit
        return np.sum(self.times >= t0)
      else: # both limits
        return np.sum((self.times >= t0) & (self.times < t1))

