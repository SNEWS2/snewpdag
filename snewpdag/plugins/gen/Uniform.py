"""
Uniform - generate a constant rate of events to add to a TimeSeries or TimeHist
Arguments:
  field:  name of field. Must be TimeSeries or TimeHist. Modified in place.
  rate:  number of events per second
  start:  starting time (seconds) of the generator.
  duration (optional, default 10s):  length of time (seconds) for generation.
    If feeding a TimeSeries, then use this to get maximum time.
    If feeding a TimeHist, use the shorter of this or TimeHist duration.
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import ns_per_second
from snewpdag.values import TimeSeries, TimeHist

class Uniform (Node):
  def __init__(self, field, rate, tmin = 0, tmax = 10, **kwargs):
    self.field = field
    self.rate = rate
    self.tmin = tmin
    self.tmax = tmax
    self.duration = kwargs.pop('duration', 10.0)
    super().__init__(**kwargs)

  def alert(self, data):
    if self.field in data:
      v = data[self.field]
      if self.tmax > self.duration:
        self.tmax = self.duration
      if self.tmin < 0:
        self.tmin = 0
      if not isinstance(v, TimeHist) and not isinstance(v, TimeSeries):
        return False # v is neither TimeHist nor TimeSeries
      mean = (self.tmax - self.tmin) * self.rate # mean number of events in the time span
      nev = Node.rng.poisson(mean) # Poisson fluctuations around mean
      u = Node.rng.integers(self.tmin * ns_per_second, self.tmax * ns_per_second, size=nev, dtype=np.int64)
      v.add_offsets(u)
      return True
    else:
      return False
