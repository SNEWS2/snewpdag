"""
Gaussian_peak - generate a gaussian_peak to add to a TimeSeries or TimeHist

Arguments:
  field:  name of field. Must be TimeSeries or TimeHist. Modified in place.
  event:  number of events to be added.
  scale:  Standard deviation (spread or “width”) of the distribution.
  expv:   Mean (“centre”)(seconds) of the distribution.
"""
import numpy as np
from snewpdag.dag import Node
from snewpdag.dag.lib import ns_per_second
from snewpdag.values import TimeSeries, TimeHist

class Gaussian_peak (Node):
  def __init__(self, field, event, scale=1, expv=2, **kwargs):
    self.field = field  
    self.event = event
    self.scale = scale
    self.expv = expv
    super().__init__(**kwargs)

  def alert(self, data):
    if self.field in data:
      v = data[self.field]
      if not isinstance(v, TimeHist) and not isinstance(v, TimeSeries):
        return False # v is neither TimeHist nor TimeSeries
      nev = Node.rng.poisson(self.event) # Poisson fluctuations
      u = Node.rng.normal(loc=self.expv * ns_per_second, scale=self.scale * ns_per_second, size=nev)
      v.add_offsets(u)
      return True
    else:
      return False

