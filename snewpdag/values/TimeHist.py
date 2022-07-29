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
    super().__init__(nb, tlow, tlow + self.duration)
    if len(data) > 0:
      self.bins = np.array(data)

  def copy(self): # deep copy
    o = TimeHist(self.start, self.duration, len(o.bins), o.bins.copy(), reference=self.reference)
    # additional Hist1D instance data
    o.overflow = self.overflow
    o.underflow = self.underflow
    o.sum = self.sum
    o.sum2 = self.sum2
    o.count = self.count
    return o

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

  def histogram(self, nbins, duration=0, start=()):
    """
    Rebin histogram.
    If old bins are divided, use linear approximation to distribute.
    """
    # slow plodding method
    w = self.duration if duration == 0 else duration
    s = self.start if start == () else self.start
    t0 = time_tuple_from_field(start)
    dt = np.array([0, w * ns_per_second / nbins], dtype='int64')
    h = np.zeros(nbins)
    for i in range(nbins):
      tlow = t0 + i * dt
      thigh = tlow + dt
      h[i] = self.integral(tlow, thigh)
    return h

  def integral(self, start=(), stop=()):
    """
    Count the events between the start and stop times.
    By default this returns the total number of events within specified range.
    If start or stop fall between bins, use linear approximation.
    """
    if start == () and stop == ():
      return np.sum(self.bins)
    else:
      dw = self.duration * ns_per_second
      w = dw / self.nbins
      i0 = 0 # take histogram start by default
      i1 = self.nbins # take histogram end by default
      under = 0 # fractional bin contents
      over = 0
      if start != ():
        t0 = time_tuple_from_field(start)
        dt = offset_from_time_tuple(subtract_time(t0, self.start))
        if dt > dw:
          return 0 # start is outside of range
        elif dt > 0:
          rem = dt % w
          i0 = int(dt / w)
          if rem == 0:
            under = 0
          else:
            under = self.bins[i0] * (w - rem) / w
            i0 += 1
      if stop != ():
        t1 = time_tuple_from_field(stop)
        dt = offset_from_time_tuple(subtract_time(t1, self.start))
        if dt <= 0:
          return 0 # end is outside of range
        elif dt < dw:
          i1 = int(dt / w)
          rem = dt % w
          if rem > 0:
            over = self.bins[i1 + 1] * rem / w
      return np.sum(self.bins[i0:i1]) + under + over

