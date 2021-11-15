"""
Skymap - render an LMap

Note that an LMap is stored in nested order.
"""
import matplotlib.pyplot as plt
import numpy as np
import healpy as hp

from snewpdag.dag import Node
from snewpdag.values import LMap

class Skymap(Node):
  def __init__(self, in_field, title, filename, **kwargs):
    self.in_field = in_field
    self.title = title
    self.filename = filename
    self.count = 0
    super().__init__(**kwargs)

  def alert(self, data):
    burst_id = data.get('burst_id', 0)
    m = data.get(self.in_field, None)
    if m:
      # replace a lot of these options later
      hp.mollview(m.map,
                  coord=["G", "E"],
                  title=self.title,
                  unit="mK",
                  norm="hist",
                  min=-1,
                  max=1,
                  nest=True,
                 )
      hp.graticule()
      fname = self.filename.format(self.name, self.count, burst_id)
      plt.savefig(fname)
      self.count += 1
    return True

