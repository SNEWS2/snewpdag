"""
BinnedAccumulator:  a plugin which accumulates a histogram of a series.

Constructor arguments:
  nbins: number of bins
  xlow: low edge of histogram
  xhigh: high edge of histogram
  in_field: string, name of field to extract from alert data
  out_xfield: name of x axis field for output data (to contain bin edges)
  out_yfield: name of y axis field for output data (to contain bin contents)
  out_field: optional, name of field for dictionary output
  flags: list of strings. Default is off for all flags.
    overflow - calculate overflow/underflow
    stats - calculate statistics

Output dictionary:
  alert:
    add count
        overflow, underflow (if 'overflow' flag)
        mean, rms (if 'stats' flag)
    delete input field
  report:
    add count
        overflow, underflow (if 'overflow' flag)
        mean, rms (if 'stats' flag)
  reset:
    forward unmodified data
  revoke:
    forward unmodified data
"""
import logging
import math
import numpy as np

from snewpdag.dag import Node

class BinnedAccumulator(Node):
  def __init__(self, in_field, nbins, xlow, xhigh,
               out_xfield, out_yfield, **kwargs):
    self.nbins = nbins
    self.xlow = xlow
    self.xhigh = xhigh
    self.field = in_field
    self.xname = out_xfield
    self.yname = out_yfield
    self.out_field = kwargs.pop('out_field', None)
    flags = kwargs.pop('flags', [])
    self.calc_overflow = 'overflow' in flags
    self.calc_stats = 'stats' in flags
    self.clear()
    super().__init__(**kwargs)

  def clear(self):
    self.bins = np.zeros(self.nbins)
    self.edges = np.zeros(self.nbins+1)
    self.overflow = 0.0
    self.underflow = 0.0
    self.sum = 0.0
    self.sum2 = 0.0
    self.count = 0
    self.changed = True

  def alert(self, data):
    vs = data[self.field]
    h, edges = np.histogram(vs, self.nbins, (self.xlow, self.xhigh))
    # note edges will have len(h)+1, since last element is top edge.
    # also note (?) that top edge is inclusive,
    # but lower bins' right edge is exclusive.
    self.edges = edges
    self.bins = self.bins + h
    self.count += len(vs)
    if self.calc_overflow:
      self.overflow += np.count_nonzero(vs > self.xhigh)
      self.underflow += np.count_nonzero(vs < self.xlow)
    if self.calc_stats:
      self.sum += np.sum(vs)
      self.sum2 += np.sum(vs*vs)
    self.changed = True
    return False

  def reset(self, data):
    return False

  def revoke(self, data):
    return False

  def report(self, data):
    if self.changed:
      d = {
            'nbins': self.nbins,
            'xlow': self.xlow,
            'xhigh': self.xhigh,
            'in_field': self.field,
            'out_xfield': self.xname,
            'out_yfield': self.yname,
            'count': self.count,
          }
      d[self.xname] = self.edges[:-1]
      d[self.yname] = self.bins
      if self.calc_overflow:
        d['overflow'] = self.overflow
        d['underflow'] = self.underflow
      if self.calc_stats:
        mean = self.sum / self.count
        d['mean'] = mean
        d['rms'] = sqrt(self.sum2 / self.count - mean*mean)
      self.changed = False
      if self.out_field == None:
        data.update(d)
      else:
        data[self.out_field] = d
      return True
    else:
      return False

