"""
ProbCL - turn a probability map into a CL map, using LIGO recipe.

Arguments:
  in_field: field name of probability values
  out_field: field name of CL values
  on (optional): list of 'alert', 'reset', 'revoke', 'report'
    (default ['alert'])

The probability values in the array will be normalized to sum to 1.

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
    self.on = kwargs.pop('on', ['alert'])
    super().__init__(**kwargs)

  def process(self, data):
    if self.in_field in data:
      h = data[self.in_field]
      m = h / np.sum(h)
      i = np.flipud(np.argsort(m))
      sorted_credible_levels = np.cumsum(m[i])
      credible_levels = np.empty_like(sorted_credible_levels)
      credible_levels[i] = sorted_credible_levels
      data[self.out_field] = 1.0 - credible_levels
      return data
    else:
      return False

  def alert(self, data):
    return self.process(data) if 'alert' in self.on else True

  def revoke(self, data):
    return self.process(data) if 'revoke' in self.on else True

  def reset(self, data):
    return self.process(data) if 'reset' in self.on else True

  def report(self, data):
    return self.process(data) if 'report' in self.on else True

