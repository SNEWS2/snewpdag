"""
ProbCL - turn a probability map into a CL map, using LIGO recipe.

Arguments:
  in_field: field name of probability values
  out_field: field name of CL values

CL values will have values from 0 (least probable) to 1 (most probable).
The 90% confidence interval will include pixels with CL > 0.9.
"""
import logging
import numpy as np

from snewpdag.dag import Node

class ProbCL(Node):
  def __init__(self, in_field, out_field, **kwargs):
    self.in_field = in_field
    self.out_field = out_field
    super().__init__(**kwargs)

  def alert(self, data):
    if self.in_field in data:
      m = data[self.in_field]
      i = np.flipud(np.argsort(m))
      sorted_credible_levels = np.cumsum(m[i])
      credible_levels = np.empty_like(sorted_credible_levels)
      credible_levels[i] = sorted_credible_levels
      data[self.out_field] = 1.0 - credible_levels
      return data
    else:
      return False

