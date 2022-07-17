"""
Hist1D - a 1D histogram value with evenly-spaced bins
(Can also hold errors in each bin, but user must explicitly set)
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
    o.errs = None if self.errs == None else self.errs.copy()
    o.overflow = self.overflow
    o.underflow = self.underflow
    o.sum = self.sum
    o.sum2 = self.sum2
    o.count = self.count
    return o

  def clear(self):
    self.bins = np.zeros(self.nbins)
    self.errs = None
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
    """
    fill histogram.  x can be a scalar or an array of fill values.
    """
    v = np.array(x)
    try:
      ix = self.nbins * (v - self.xlow) / self.xwidth
    except:
      logging.info('Hist1D: index calculation error {}'.format(sys.exc_info()))
      return
    h, bin_edges = np.histogram(ix, bins=self.nbins, range=(0, self.nbins))
    self.bins += h
    self.underflow += weight * np.sum(ix < 0)
    self.overflow += weight * np.sum(ix >= self.nbins)
    self.sum += np.sum(v)
    self.sum2 += np.sum(v*v)
    self.count += weight * v.size

  def mean(self):
    return self.sum / self.count

  def variance(self):
    x = self.mean()
    xx = self.sum2 / self.count
    return xx - x*x

