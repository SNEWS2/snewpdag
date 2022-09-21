"""
Uniform - generate a constant rate of events to add to a TSeries or THist
Arguments:
  field:  name of field. Must be TSeries or THist. Modified in place.
  rate:  number of events per second
  tmin:  start time (seconds, relative to reference time)
  tmax:  stop time (seconds, relative to reference time)
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
    self.tmin = np.int64(tmin * ns_per_second) # ns
    self.tmax = np.int64(tmax * ns_per_second) # ns
    self.mean_total = (tmin - tmax) * rate
    super().__init__(**kwargs)

  def alert(self, data):
    if self.field in data:
      v = data[self.field]
      if not isinstance(v, THist) and not isinstance(v, TSeries):
        logging.error('Uniform.alert: field is neither THist nor TSeries')
        return False # v is neither THist nor TSeries

      # suggested optimizations:
      # * THist can be filled bin-by-bin with Poisson variates
      #   mu = rate * duration / v.nbins
      #   v.bins += Node.rng.poisson(mu, v.nbins)
      #   (but need to adjust means for partial bins at ends)
      # * for THist and TSeries with limits, can restrict generation
      #   to within those limits, rather than over the whole (tmin,tmax)

      nev = Node.rng.poisson(self.mean) # Poisson fluctuations around mean
      u = Node.rng.integers(self.tmin, self.tmax, size=nev, dtype=np.int64)
      v.add_offsets(u) # assumes seconds
      return True
    else:
      return False

