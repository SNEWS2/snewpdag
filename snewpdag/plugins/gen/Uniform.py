"""
Uniform - generate a constant rate of events to add to a TimeSeries or TimeHist

Arguments:
  field:  name of field. Must be TimeSeries or TimeHist. Modified in place.
  rate:  number of events per second
  time_span (optional):  length of time (seconds) for generation.
    If feeding a TimeSeries, then use this to get maximum time.
    If feeding a TimeHist, use the shorter of this or TimeHist time_span.
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.values import TimeSeries, TimeHist

class Uniform (Node):
  def __init__(self, field, rate, **kwargs):
    self.field = field
    self.rate = rate
    self.time_span = kwargs.pop('time_span', 0.0)
    super().__init__(**kwargs)

  def alert(self, data):
    if self.field in data:
      v = data[self.field]
      dt = self.time_span
      if isinstance(v, TimeHist):
        if dt == 0.0 or dt > v.time_span:
          dt = v.time_span
      else if not isinstance(v. TimeSeries):
        return False # v is neither TimeHist nor TimeSeries
      mean = dt * self.rate # mean number of events in the time span
      nev = Node.rng.poisson(mean) # Poisson fluctuations around mean
      u = Node.rng.integers(0, dt * ns_per_second, size=nev, dtype=np.int64)
      v.add_offsets(u)
    else:
      return False

