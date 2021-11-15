"""
Mollview
"""
import matplotlib.pyplot as plt
import numpy as np
import healpy as hp

from snewpdag.dag import Node
from snewpdag.values import LMap

class Mollview(Node):
  def __init__(self, in_field, title, units, coord, filename, **kwargs):
    self.in_field = in_field
    self.title = title
    self.units = units
    self.coord = coord
    self.filename = filename
    self.min = kwargs.pop('min', 1)
    self.max = kwargs.pop('max', 1)
    self.count = 0
    super().__init__(**kwargs)

  def alert(self, data):
    burst_id = data.get('burst_id', 0)
    if self.in_field in data:
      m = data[self.in_field]
      # replace a lot of these options later
      hp.mollview(m,
                  coord=self.coord,
                  title=self.title,
                  unit=self.units,
                  min=self.min,
                  max=self.max,
                  nest=True,
                 )
      hp.graticule()
      fname = self.filename.format(self.name, self.count, burst_id)
      plt.savefig(fname)
      self.count += 1
    return True

