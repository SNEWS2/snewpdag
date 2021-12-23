"""
NormHistogram - normalize histogram to some area

Arguments:
  in_field: name of input field to normalize
  out_field: name of output field, after normalization
  area: (optional) area to normalize to

Input payload:
  in_field: histogram to normalize

Output payload:
  out_field: normalized histogram
"""
import logging
import numpy as np

from snewpdag.dag import Node

class NormHistogram(Node):
  def __init__(self, in_field, out_field, **kwargs):
    self.area = kwargs.pop('area', 1.0)
    self.in_field = in_field
    self.out_field = out_field
    super().__init__(**kwargs)

  def alert(self, data):
    if self.in_field in data:
      m = np.array(data[self.in_field])
      data[self.out_field] = m * self.area / np.sum(m)
      return data
    else:
      return False

