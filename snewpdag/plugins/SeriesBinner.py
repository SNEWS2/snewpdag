"""
SeriesBinner:  a plugin which turns a series into a histogram for each alert.

  An alert action bins the input time series and forwards the result
  for the single alert.

  A report action forwards the accumulated histogram.
  (ignored if accumulate option is false)

  A reset action does nothing, since the reset action is supposed to
  clear the way for new alerts, whereas the alert action of this plugin is
  stateless.

Constructor arguments:
  nbins: number of bins
  xlow: low edge of histogram
  xhigh: high edge of histogram
  field: string, name of field to extract from alert data
  xname: name of x axis field for output data (to contain bin edges)
  yname: name of y axis field for output data (to contain bin contents)
  flags: list of strings. Default is off for all flags.
    accumulate - accumulate over alerts, clear after report
    overflow - calculate overflow/underflow
    stats - calculate statistics

Output json:
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

class SeriesBinner(Node):
  def __init__(self, field, nbins, xlow, xhigh, xname, yname, **kwargs):
    self.nbins = nbins
    self.xlow = xlow
    self.xhigh = xhigh
    self.field = field
    self.xname = xname
    self.yname = yname
    self.accumulate = False
    self.calc_overflow = False
    self.calc_stats = False
    if 'flags' in kwargs:
      flags = kwargs['flags']
      self.accumulate = 'accumulate' in flags
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

  def update(self, data):
    action = data['action']
    ndata = { 'nbins': self.nbins, 'xlow': self.xlow, 'xhigh': self.xhigh,
              'field': self.field, 'xname': self.xname, 'yname': self.yname }

    if action == 'alert':
      vs = data[self.field]
      h, edges = np.histogram(vs, self.nbins, (self.xlow, self.xhigh))
      # note edges will have len(h)+1, since last element is top edge.
      # also note (?) that top edge is inclusive,
      # but lower bins' right edge is exclusive.
      self.edges = edges
      ndata = data.copy()
      ndata[self.xname] = edges[:-1]
      ndata[self.yname] = h
      n = len(vs)
      ndata['count'] = n

      if self.calc_overflow:
        ovf = np.count_nonzero(vs > self.xhigh)
        unf = np.count_nonzero(vs < self.xlow)
        ndata['overflow'] = ovf
        ndata['underflow'] = unf
      if self.calc_stats:
        s = np.sum(vs)
        s2 = np.sum(vs*vs)
        mean = s / n
        ndata['mean'] = mean
        ndata['rms'] = sqrt(s2 / n - mean*mean)

      if self.accumulate:
        self.bins = self.bins + h
        self.count += n
        if self.calc_overflow:
          self.overflow += ovf
          self.underflow += unf
        if self.calc_stats:
          self.sum += s
          self.sum2 += s2

      del ndata[self.field] # delete time series from data
      self.notify(action, None, ndata)

    elif action == 'report':
      if self.accumulate:
        ndata['count'] = self.count
        ndata[self.xname] = self.edges[:-1]
        ndata[self.yname] = self.bins # do I need to copy?
        if self.calc_overflow:
          ndata['overflow'] = self.overflow
          ndata['underflow'] = self.underflow
        if self.calc_stats:
          mean = self.sum / self.count
          ndata['mean'] = mean
          ndata['rms'] = sqrt(self.sum2 / self.count - mean*mean)
        data.update(ndata)
      self.notify(action, None, data)

    elif action == 'reset' or action == 'revoke':
      #self.reset() # do nothing, but still forward
      self.notify(action, None, data)

