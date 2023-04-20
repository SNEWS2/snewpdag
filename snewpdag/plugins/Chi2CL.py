"""
Chi2CL - take a chi2 map and turn it into CL

arguments:
  in_field: field name of chi2 values
  in_ndof_field: field name of ndof value
  out_field: field name of probability values

Note that chi2 is calculated at the center of each pixel (in DiffPointing),
and the calculation here takes the confidence level of each pixel as 1 minus
the corresponding cdf.  By definition, the pixel with the minimum chi2
will have level 1.0.  Pixels within a certain confidence level will be
those whose cdf at the pixel center exceed the given level.
"""
import logging
import numpy as np
from scipy.stats import chi2

from snewpdag.dag import Node

class Chi2CL(Node):
  def __init__(self, in_field, in_ndof_field, out_field, **kwargs):
    self.in_field = in_field
    self.in_ndof_field = in_ndof_field
    self.out_field = out_field
    super().__init__(**kwargs)

  def alert(self, data):
    if self.in_field in data:
      #m = np.array(data[self.in_field])
      #base = np.min(m)
      #v = m - base
      v = np.array(data[self.in_field])
      c = chi2.cdf(v, df=data[self.in_ndof_field])
      data[self.out_field] = 1.0 - c
      logging.info('chi2 range ({}, {}), ndof = {}'.format(np.min(v), np.max(v), data[self.in_ndof_field]))
      return data
    else:
      return False

