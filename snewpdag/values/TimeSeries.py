"""
TimeSeries - a series of events

We use the time tuples (s,ns) of snewpdag.dag.lib.
This assumes a conversion from date/time has already taken place,
and we're using time as understood internally by SNEWS,
i.e., the s field is seconds after some date.
"""
import logging
import numpy as np
from snewpdag.dag.lib import normalize_time, subtract_time, ns_per_second, time_tuple_from_float

class TimeSeries:
  def __init__(self, start, duration=0, offsets=[]):
    """
    start:  float or (s,ns)
    duration:  duration of span in seconds, or 0 if indeterminate
    offsets (optional):  ns offsets from start
    """
    if np.isscalar(start):
      self.start = time_tuple_from_float(start)
    else:
      self.start = np.array(start)
    self.duration = duration
    self.times = np.array([], dtype=np.int64)
    if len(offsets) > 0:
      if duration == 0:
        self.times = np.sort(np.append(self.times, offsets))
      else:
        self.times = np.sort(np.append(self.times, \
                             offsets[offsets < duration * ns_per_second]))

  def add_offsets(self, offsets):
    """
    offsets:  an array of ns offsets from start time
    """
    if self.duration == 0:
      self.times = np.sort(np.append(self.times, offsets))
    else:
      self.times = np.sort(np.append(self.times, \
                           offsets[offsets < duration * ns_per_second]))

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

  def event(self, index):
    """
    get the normalized (s,ns) time of indexed event(s).
    if index is a simple number, just return one result.
    if index is an array of indices, return corresponding results in array.
    """
    try:
      if np.isscalar(index):
        t1 = np.add(self.start, (0, self.times[index]))
      else:
        i = np.array(index)
        t0 = np.full((len(i), 2), self.start)
        dt = np.column_stack((np.zeros(len(i)), self.times[i]))
        t1 = t0 + dt
    except IndexError:
      logging.error('TimeSeries: index out of bounds')
      return None
    else:
      return normalize_time(t1)

