"""
SeriesBinner:  a plugin which turns a series into a histogram for each alert.

  An alert action bins the input time series and forwards the result
  for the single alert.

  Other actions don't do anything except forward, since this
  calculation is essentially stateless.

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

Output json:
  alert:
    add count
        overflow, underflow (if 'overflow' flag)
        mean, rms (if 'stats' flag)
"""
import logging
import numpy as np

from snewpdag.dag import Node

class SeriesBinner(Node):
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
    super().__init__(**kwargs)
    self.clear()

  def clear(self):
    self.bins = np.zeros(self.nbins)
    self.edges = np.zeros(self.nbins+1)
    self.overflow = 0.0
    self.underflow = 0.0
    self.sum = 0.0
    self.sum2 = 0.0
    self.count = 0

  def alert(self, data):
    d = {
          'nbins': self.nbins,
          'xlow': self.xlow,
          'xhigh': self.xhigh,
          'in_field': self.field,
          'out_xfield': self.xname,
          'out_yfield': self.yname,
          'count': self.count,
        }
    vs = data[self.field]
    h, edges = np.histogram(vs, self.nbins, (self.xlow, self.xhigh))
    # note edges will have len(h)+1, since last element is top edge.
    # also note (?) that top edge is inclusive,
    # but lower bins' right edge is exclusive.
    d[self.xname] = edges[:-1]
    d[self.yname] = h
    n = len(vs)
    d['count'] = n
    if self.calc_overflow:
      d['overflow'] = np.count_nonzero(vs > self.xhigh)
      d['underflow'] = np.count_nonzero(vs < self.xlow)
    if self.calc_stats:
      s = np.sum(vs)
      s2 = np.sum(vs*vs)
      mean = s / n
      d['mean'] = mean
      d['rms'] = sqrt(s2 / n - mean*mean)
    if self.out_field == None:
      data.update(d)
    else:
      data[self.out_field] = d
    return True

