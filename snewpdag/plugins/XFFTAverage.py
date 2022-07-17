"""
XFFTAverage - analysis plugin for XFFT trials

Arguments:
  in_field:  input field name for FT to analyze
  out_avg_field:  output field for phase averages

Input data:

Output data:

"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field
from snewpdag.values import Hist1D

class XFFTAverage(Node):
  def __init__(self, in_field, out_avg_field, **kwargs):
    self.in_field = in_field
    self.out_avg_field = out_avg_field
    self.count = 0 # number of trials accumulated
    super().__init__(**kwargs)

  def alert(self, data):
    ft, flag = fetch_field(data, self.in_field)
    if flag:
      if self.count == 0:
        self.sy = np.zeros(len(ft)) # sums in each bin
        self.ssy = np.zeros(len(ft)) # sums of squares in each bin
      phi = np.angle(ft)
      self.sy += phi
      self.ssy += phi * phi
      self.count += 1
    return False

  def report(self, data):
    h = Hist1D(len(self.sy), 0, len(self.sy))
    h.bins = self.sy / self.count
    h.errs = np.sqrt(self.ssy - self.sy * self.sy) / self.count
    data[self.out_avg_field] = h
    return data

