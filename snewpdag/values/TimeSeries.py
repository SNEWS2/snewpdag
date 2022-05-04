"""
TimeSeries - a series of events

We use the time tuples (s,ns) of snewpdag.dag.lib.
This assumes a conversion from date/time has already taken place,
and we're using time as understood internally by SNEWS,
i.e., the s field is seconds after some date.
"""
import logging
import numpy as np
from snewpdag.dag.lib import normalize_time, subtract_time

class TimeSeries:
  def __init__(self, start_time, start_ns):
    """
    start_time:  a datetime object
    start_ns:  ns offset after start_time
    """
    self.start = np.array([start_time, start_ns])
    self.times = np.array([])

  def add_offsets(self, offsets):
    """
    offsets:  an array of ns offsets from start time
    """
    np.append(self.times, offsets)
    np.sort(self.times)

  def add_times(self, times):
    """
    times:  an array of (s,ns) times.  Subtract start time before storing.
    """
    g = 1000000000
    if np.shape(times)[-1] < 2:
      logging.error("input array has wrong shape {}".format(np.shape(times)))
      return
    d = subtract_time(times, self.start)
    b = np.array(d, 2) # [0] should be s, [1] should be ns
    offsets = g * b[0] + b[1]
    self.add_offsets(offsets)

  def event(self, index):
    """
    get the normalized (s,ns) time of indexed event(s).
    if index is a simple number, just return one result.
    if index is an array of indices, return corresponding results in array.
    """
    if np.isscalar(index):
      i = np.array([index])
    else:
      i = np.array(index)
    t0 = np.full((len(index), 2), self.start)
    dt = np.column_stack(np.zeros(len(index)), self.times[index])
    t1 = t0 + dt
    return normalize_time(t1)

