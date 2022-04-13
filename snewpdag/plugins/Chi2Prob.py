"""
Chi2Prob - take a chi2 map and turn it into probability map

arguments:
  in_field: field name of chi2 values
  out_field: field name of probability values

The probability map is normalized to unit area
"""
import logging
import numpy as np
from scipy.stats import chi2

from snewpdag.dag import Node

class Chi2Prob(Node):
  def __init__(self, in_field, out_field, **kwargs):
    self.in_field = in_field
    self.out_field = out_field
    super().__init__(**kwargs)

  def alert(self, data):
    if self.in_field in data:
      m = np.array(data[self.in_field])
      base = np.min(m)
      v = m - base
      c = chi2.pdf(v, df=2)
      sc = np.sum(c)
      logging.info('Sum of probability map is {}'.format(sc))
      data[self.out_field] = c / sc
      return data
    else:
      return False

