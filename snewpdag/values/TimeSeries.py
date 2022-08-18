"""
TimeSeries - a series of events

We use the time tuples (s,ns) of snewpdag.dag.lib.
This assumes a conversion from date/time has already taken place,
and we're using time as understood internally by SNEWS,
i.e., the s field is seconds after some date.
"""
import logging
import numpy as np
from snewpdag.dag.lib import normalize_time, subtract_time, ns_per_second, time_tuple_from_float, time_tuple_from_field, offset_from_time_tuple

class TimeSeries:
  def __init__(self, start, duration=0, offsets=[], **kwargs):
    """
    start:  float or (s,ns)
    reference (optional):  float or (s,ns). Defines t=0.
      Default is the same as start_time.
    duration:  duration of span in seconds, or 0 if indeterminate
    offsets (optional):  ns offsets from start
    """
    self.start = time_tuple_from_field(start)
    reft = kwargs.pop('reference', start)
    self.reference = time_tuple_from_field(reft)
    self.duration_ns = duration * ns_per_second
    self.start_offset_ns = offset_from_time_tuple( \
                           subtract_time(self.start, self.reference)) \
                           * ns_per_second
    self.stop_offset_ns = self.start_offset_ns + self.duration_ns
    self.times = np.array([], dtype=np.int64)
    if len(offsets) > 0:
      if self.duration_ns == 0:
        self.times = np.sort(np.append(self.times, offsets))
      else:
        self.times = np.sort(np.append(self.times, \
                             offsets[(offsets > self.start_offset_ns) & \
                                     (offsets < self.stop_offset_ns)]))

  def copy(self): # deep copy
    o = TimeSeries(self.start, self.duration_ns / ns_per_second,
                   self.times.copy(), reference=self.reference)
    return o

  def to_dict(self):
    return { 'start': [ int(self.start[0]), int(self.start[1]) ],
             'reference': [ int(self.reference[0]), int(self.reference[1]) ],
             'duration': self.duration_ns / ns_per_second,
             'times': [ t for t in self.times ],
           }

  def add_offsets(self, offsets):
    """
    offsets:  an array of ns offsets from start time
    """
    if self.duration_ns == 0:
      self.times = np.sort(np.append(self.times, offsets))
    else:
      self.times = np.sort(np.append(self.times, \
                           offsets[(offsets > self.start_offset_ns) & \
                                   (offsets < self.stop_offset_ns)]))

  def add_offsets_s(self, offsets):
    """
    offsets:  an array of offsets (in seconds) from start time
    """
    dt = np.array(offsets) * ns_per_second
    self.add_offsets(dt)

  def add_offsets_ms(self, offsets):
    """
    offsets:  an array of offsets (in ms) from start time
    """
    dt = np.array(offsets) * (ns_per_second / 1000)
    self.add_offsets(dt)

  def add_times(self, times):
    """
    times:  an array of times.  Subtract reference time before appending.
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
      tt = ts
    elif shape == () or len(shape) == 1:
      # array or scalar of s in float
      tt = time_tuple_from_float(ts)
    else:
      logging.error("input array has wrong shape {}".format(shape))
      return
    d = subtract_time(tt, self.reference)
    t = np.multiply(d[...,0], ns_per_second, dtype=np.int64)
    t = np.add(t, d[...,1], dtype=np.int64)
    self.add_offsets(t)

  def event(self, index):
    """
    get the normalized (s,ns) time of indexed event(s).
    if index is a simple number, just return one result.
    if index is an array of indices, return corresponding results in array.
    """
    try:
      if np.isscalar(index):
        t1 = np.add(self.reference, (0, self.times[index]))
      else:
        i = np.array(index)
        t0 = np.full((len(i), 2), self.reference)
        dt = np.column_stack((np.zeros(len(i)), self.times[i]))
        t1 = t0 + dt
    except IndexError:
      logging.error('TimeSeries: index out of bounds')
      return None
    else:
      return normalize_time(t1)

  def histogram(self, nbins, duration=0, start=()):
    """
    Make a histogram out of the time series.
    The histogram's low edge will be the start time.
    The defaults for duration and start are those of the TimeSeries itself.
    if ref time is 100s, but requested start time is 90s, then
    all offsets need to add 10s before making the histogram.

    Returns histogram, bin edges
    """
    width = self.duration_ns if duration == 0 else duration * ns_per_second
    t0 = self.start if start == () else time_tuple_from_field(start)
    offset = offset_from_time_tuple(subtract_time(self.reference, t0))
    h, edges = np.histogram(self.times + offset, bins=nbins, range=(0, width))
    return h

  def integral(self, start=(), stop=()):
    """
    Count the events between the start and stop times.
    By default this returns the total number of events.
    """
    if start == () and stop == ():
      return self.times.size
    else:
      if start == ():
        ts0 = self.times
      else:
        t0 = time_tuple_from_field(start)
        off0 = offset_from_time_tuple(subtract_time(t0, self.reference))
        ts0 = self.times[self.times >= off0]
      if stop == ():
        ts1 = ts0
      else:
        t1 = time_tuple_from_field(stop)
        off1 = offset_from_time_tuple(subtract_time(t1, self.reference))
        ts1 = ts0[ts0 < off1]
      return ts1.size

