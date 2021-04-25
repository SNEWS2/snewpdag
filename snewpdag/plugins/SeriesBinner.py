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
  field: string, name of field to extract from alert data
  xname: name of x axis field for output data (to contain bin edges)
  yname: name of y axis field for output data (to contain bin contents)
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
import math
import numpy as np

from snewpdag.dag import Node

class SeriesBinner(Node):
  def __init__(self, field, nbins, xlow, xhigh, xname, yname, **kwargs):
    self.nbins = nbins
    self.xlow = xlow
    self.xhigh = xhigh
    self.field = field
    self.xname = xname
    self.yname = yname
    self.calc_overflow = False
    self.calc_stats = False
    if 'flags' in kwargs:
      flags = kwargs['flags']
      self.calc_overflow = 'overflow' in flags
      self.calc_stats = 'stats' in flags
      kwargs.pop('flags')
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

  def alert(self, data):
    data['nbins'] = self.nbins
    data['xlow'] = self.xlow
    data['xhigh'] = self.xhigh
    data['field'] = self.field
    data['xname'] = self.xname
    data['yname'] = self.yname
    data['count'] = self.count
    vs = data[self.field]
    h, edges = np.histogram(vs, self.nbins, (self.xlow, self.xhigh))
    # note edges will have len(h)+1, since last element is top edge.
    # also note (?) that top edge is inclusive,
    # but lower bins' right edge is exclusive.
    data[self.xname] = edges[:-1]
    data[self.yname] = h
    n = len(vs)
    data['count'] = n
    if self.calc_overflow:
      data['overflow'] = np.count_nonzero(vs > self.xhigh)
      data['underflow'] = np.count_nonzero(vs < self.xlow)
    if self.calc_stats:
      s = np.sum(vs)
      s2 = np.sum(vs*vs)
      mean = s / n
      data['mean'] = mean
      data['rms'] = sqrt(s2 / n - mean*mean)
    return data

