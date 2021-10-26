"""
Chi2CL - take a chi2 map and turn it into CL
"""
import logging
import numpy as np
from scipy.stats import chi2

from snewpdag.dag import Node

class Chi2CL(Node):
  def __init__(self, in_field, out_field, **kwargs):
    self.in_field = in_field
    self.out_field = out_field
    super().__init__(**kwargs)

  def alert(self, data):
    if self.in_field in data:
      m = np.array(data[self.in_field])
      base = np.min(m)
      v = m - base
      c = chi2.cdf(v, df=2)
      data[self.out_field] = 1.0 - c
      return data
    else:
      return False

