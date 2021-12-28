"""
AccHistogram - accumulate histogram

Arguments:
  in_field: name of input field to accumulate
  out_field: name of output field on report

Input payload:
  in_field: histogram to add.
  Consumes alert.

Output payload (report only):
  out_field: normalized histogram
"""
import logging
import numpy as np

from snewpdag.dag import Node

class AccHistogram(Node):
  def __init__(self, in_field, out_field, **kwargs):
    self.m = np.array([])
    self.in_field = in_field
    self.out_field = out_field
    super().__init__(**kwargs)

  def alert(self, data):
    if self.in_field in data:
      if len(self.m) == 0:
        self.m = np.zeros(len(data[self.in_field]))
      elif len(data[self.in_field]) != len(self.m):
        logging.warning('{}: unequal histogram sizes'.format(self.name))
        return False
      self.m += data[self.in_field]
    return False

  def report(self, data):
    data[self.out_field] = self.m
    return data

