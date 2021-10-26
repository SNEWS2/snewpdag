"""
Mollview
"""
import matplotlib.pyplot as plt
import numpy as np
import healpy as hp

from snewpdag.dag import Node
from snewpdag.values import LMap

class Mollview(Node):
  def __init__(self, in_field, title, filename, **kwargs):
    self.in_field = in_field
    self.title = title
    self.filename = filename
    super().__init__(**kwargs)

  def alert(self, data):
    if self.in_field in data:
      m = data[self.in_field]
      # replace a lot of these options later
      hp.mollview(m,
                  coord=["G", "E"],
                  title=self.title,
                  unit="CL",
                  min=0,
                  max=1,
                  nest=True,
                 )
      hp.graticule()
      plt.savefig(self.filename)
    return True

