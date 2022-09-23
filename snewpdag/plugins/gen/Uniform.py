"""
Uniform - generate a constant rate of events to add to a TimeSeries or Hist1D
Arguments:
  field:  field specifier. Must be TimeSeries or Hist1D. Modified in place.
  rate:  number of events per second
  tmin:  starting time (seconds) of the generator.
  tmax:  stopping time (seconds).
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.values import TimeSeries, Hist1D

class Uniform (Node):
  def __init__(self, field, rate, tmin, tmax, **kwargs):
    self.field = field
    self.rate = rate
    self.tmin = tmin
    self.tmax = tmax
    self.mean_total = (tmax - tmin) * rate
    super().__init__(**kwargs)

  def alert(self, data):
    v, flag = fetch_field(data, self.field)
    if flag:
      v = data[self.field]
      if not isinstance(v, TimeSeries) and not isinstance(v, Hist1D):
        logging.error('Uniform.alert: field is neither TimeSeries nor Hist1D')
        return False

      # suggested optimizations:
      # * Hist1D can be filled bin by bin with Poisson variates
      #   mu = self.rate * v.duration / v.nbins
      #   v.bins += Node.rng.poisson(mu, v.nbins)
      #   (but need to adjust means for partial bins at ends)
      # * for Hist1D, and TimeSeries with limits, can restrict generation
      #   to within those limits, rather than over the whole (tmin,tmax) 

      nev = Node.rng.poisson(self.mean_total) # Poisson fluctuations around mean
      u = Node.rng.integers(self.tmin, self.tmax, size=nev, dtype=np.float64)
      v.add(u)
      return True
    else:
      return False
