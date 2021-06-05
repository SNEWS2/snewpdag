"""
Hist1D - a 1D histogram value with evenly-spaced bins
"""
import logging
import numpy as np

class Hist1D:
  def __init__(self, nbins, xlow, xhigh):
    self.nbins = nbins
    self.xlow = xlow
    self.xhigh = xhigh
    self.xwidth = xhigh - xlow
    self.clear()

  # deep copy
  def copy(self):
    o = Hist1D(self.nbins, self.xlow, self.xhigh)
    o.bins = self.bins.copy()
    o.overflow = self.overflow
    o.underflow = self.underflow
    o.sum = self.sum
    o.sum2 = self.sum2
    o.count = self.count
    return o

  def clear(self):
    self.bins = np.zeros(self.nbins)
    self.overflow = 0.0
    self.underflow = 0.0
    self.sum = 0.0
    self.sum2 = 0.0
    self.count = 0

  def is_compatible(self, other):
    if isinstance(other, Hist1D):
      return self.nbins == other.nbins and \
             self.xlow == other.xlow and \
             self.xhigh == other.xhigh
    else:
      return False

  def fill(self, x, weight=1.0):
    try:
      ix = int(self.nbins * (x - self.xlow) / self.xwidth)
    except:
      logging.info('Hist1D: index calculation error {}'.format(sys.exc_info()))
      return
    if ix < 0:
      self.underflow += weight
    elif ix >= self.nbins:
      self.overflow += weight
    else:
      self.bins[ix] += weight
    self.sum += x
    self.sum2 += x*x
    self.count += weight

  def mean(self):
    return self.sum / self.count

  def variance(self):
    x = self.mean()
    xx = self.sum2 / self.count
    return xx - x*x

