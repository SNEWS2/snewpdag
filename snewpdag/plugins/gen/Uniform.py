"""
Uniform - generate a constant rate of events to add to a TSeries or THist
Arguments:
  field:  name of field. Must be TSeries or THist. Modified in place.
  rate:  number of events per second
  start:  starting time (seconds) of the generator.
  duration (optional, default 10s):  length of time (seconds) for generation.
    If feeding a TSeries, then use this to get maximum time.
    If feeding a THist, use the shorter of this or THist duration.
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import ns_per_second
from snewpdag.values import TSeries, THist

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
      # TODO: need to fix this when THist/TSeries have common base
      #dt = self.duration
      #if isinstance(v, THist):
      #  if dt <= 0.0 or dt > v.duration:
      #    #dt = v.duration # use full duration
      #    # actually, we have a simpler way of generating in this case
      #    # (THist, over whole range), adding Poisson fluctuations
      #    # to each bin
      #    mu = self.rate * v.duration / v.nbins
      #    v.bins += Node.rng.poisson(mu, v.nbins)
      #    return True
      #elif not isinstance(v, TSeries):
      if self.tmax > self.duration:
        self.tmax = self.duration
      if self.tmin < 0:
        self.tmin = 0
      if not isinstance(v, THist) and not isinstance(v, TSeries):
        return False # v is neither THist nor TSeries
      mean = (self.tmax - self.tmin) * self.rate # mean number of events in the time span
      nev = Node.rng.poisson(mean) # Poisson fluctuations around mean
      u = Node.rng.integers(self.tmin, self.tmax, size=nev, dtype=np.int64)
      u = (self.tmax - self.tmin) * Node.rng.random(size=nev) + self.tmin
      v.add_offsets(u) # assumes seconds
      return True
    else:
      return False

