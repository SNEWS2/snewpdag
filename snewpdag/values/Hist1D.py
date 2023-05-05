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

  def clear(self):
    self.bins = np.zeros(self.nbins)
    self.overflow = 0.0
    self.underflow = 0.0
    self.sum = 0.0
    self.sum2 = 0.0
    self.count = 0

  def copy(self):
    h = Hist1D(self.nbins, self.xlow, self.xhigh)
    h.bins = self.bins.copy()
    h.overflow = self.overflow
    h.underflow = self.underflow
    h.sum = self.sum
    h.sum2 = self.sum2
    h.count = self.count
    return h

  def is_compatible(self, other):
    if isinstance(other, Hist1D):
      return self.nbins == other.nbins and \
             self.xlow == other.xlow and \
             self.xhigh == other.xhigh
    else:
      return False

  def to_dict(self):
    d = {
          'xlow': self.xlow,
          'xhigh': self.xhigh,
          'count': self.count,
          'sum': self.sum,
          'sum2': self.sum2,
          'underflow': self.underflow,
          'overflow': self.overflow,
          'bins': self.bins.copy()
        }

  def bin_index(self, x):
    """
    Return bin index for a given x.
    Doesn't really worry about range, so
    underflow is anything engative,
    and overflow is a number >= nbins
    """
    try:
      return np.int(self.nbins * (x - self.xlow) / self.xwidth)
    except:
      logging.info('Hist1D.bin: index calc error {}'.format(sys.exc_info()))
      return None

  def bin_edge(self, index):
    """
    Return low edge of bin
    """
    dx = self.width / len(self.bins)
    return self.xlow + index * dx

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

  def add(self, x, weight=1.0):
    """
    Synonym of fill(), same signature as in TimeSeries
    """
    self.fill(x, weight)

  def mean(self):
    return 0.0 if self.count == 0 else self.sum / self.count

  def variance(self):
    if self.count == 0:
      return 0.0
    else:
      x = self.mean()
      xx = self.sum2 / self.count
      return xx - x*x

  def histogram(self, nbins, xlow=None, xhigh=None):
    """
    Rebin histogram.
    """
    x0 = self.xlow if xlow == None else xlow
    x1 = self.xhigh if xhigh == None else xhigh
    js = self.bin_edge(np.linspace(x0, x1, num=nbins, endpoint=False))
    m = (js >= 0) & (js < self.nbins)
    ks = js[m]
    h = np.zeros(nbins)
    for i in range(len(ks)):
      h[ks[i]] += self.bins[i]
    return h

  def integral(self, xlow=None, xhigh=None):
    """
    Count events in bins between xlow and xhigh (if given).
    Gives best approximation based on closest bin edges.
    """
    x0 = self.xlow if xlow == None else xlow
    x1 = self.xhigh if xhigh == None else xhigh
    if x0 == self.xlow and x1 == self.xhigh:
      return np.sum(self.bins)
    else:
      i0 = np.round((x0 - self.xlow) * self.nbins / self.xwidth)
      i1 = np.round((x1 - self.xhigh) * self.nbins / self.xwidth)
      return np.sum(self.bins[i0:i1])

