"""
GaussianPeak - generate a gaussian_peak to add to a TimeSeries or Hist1D

Arguments:
  field:  field specifier. Must be TimeSeries or Hist1D. Modified in place.
  event:  number of events to be added.
  stdev:  Standard deviation (spread or “width”) of the distribution.
  expv:   Expected value (“centre”)(seconds) of the distribution.
"""
import numpy as np
from snewpdag.dag import Node
from snewpdag.values import TimeSeries, Hist1D
from snewpdag.dag.lib import fetch_field

class GaussianPeak (Node):
  def __init__(self, field, event, stdev=1, expv=2, **kwargs):
    self.field = field  
    self.event = event
    self.stdev = stdev
    self.expv = expv
    super().__init__(**kwargs)

  def alert(self, data):
    v, flag = fetch_field(data, self.field)
    if flag:
      if not isinstance(v, Hist1D) and not isinstance(v, TimeSeries):
        return False # v is neither TimeHist nor TimeSeries
      nev = Node.rng.poisson(self.event) # Poisson fluctuations
      u = Node.rng.normal(loc=self.expv, scale=self.stdev, size=nev)
      v.add(u)
      return True
    else:
      return False

