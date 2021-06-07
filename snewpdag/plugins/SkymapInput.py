"""
SkymapInput - read a healpix skymap from a file
"""
import logging
import numpy as np
import healpy as hp

from snewpdag.dag import Node
from snewpdag.values import LMap

class SkymapInput(Node):
  def __init__(self, filename, out_field, **kwargs):
    self.out_field = out_field
    m = hp.read_map(filename, nest=True)
    self.map = LMap(m)
    super().__init__(**kwargs)

  def alert(self, data):
    data[self.out_field] = self.map.copy()
    return True

