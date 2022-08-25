"""
FillHist1D:  a plugin which accumulates a histogram based on its configuration.
  Only notifies downstream plugins on a `report' action.

Constructor arguments:
  nbins: number of bins
  xlow: low edge of histogram
  xhigh: high edge of histogram
  in_field: input field specifier
  out_field: output field

Output json:
  alert:  no output
  reset:  no output
  revoke:  no output
  report:  add (out_field)
"""
import sys
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field
from snewpdag.values import Hist1D

class FillHist1D(Node):
  def __init__(self, nbins, xlow, xhigh, in_field, out_field, **kwargs):
    self.hist = Hist1D(nbins, xlow, xhigh)
    self.in_field = in_field
    self.out_field = out_field
    super().__init__(**kwargs)

  def clear(self):
    self.hist.clear()

  def alert(self, data):
    v, flag = fetch_field(data, self.in_field)
    if not flag:
      logging.error('{}: field {} not found'.format(self.name, self.in_field))
      return False
      return
    self.hist.fill(v)
    return False # don't forward an alert

  def reset(self, data):
    return False

  def revoke(self, data):
    return False

  def report(self, data):
    data[self.out_field] = self.hist.copy()
    return True

