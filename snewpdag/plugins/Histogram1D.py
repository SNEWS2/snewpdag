"""
Histogram1D:  a plugin which accumulates a histogram based on its configuration.
  Only notifies downstream plugins on a `report' action.

Constructor arguments:
  nbins: number of bins
  xlow: low edge of histogram
  xhigh: high edge of histogram
  field: string, name of field to extract from alert data
  index: int or tuple (from list), element numbers if field is an array
  index2: secondary index if needed (e.g., if a 2D array or dict)

(Could also specify variable-width bins?)
"""
import logging
import numpy as np

from snewpdag.dag import Node

class Histogram1D(Node):
  def __init__(self, nbins, xlow, xhigh, field, **kwargs):
    self.nbins = nbins
    self.xlow = xlow
    self.xhigh = xhigh
    self.field = field
    self.index = None
    self.index2 = None
    if 'index' in kwargs:
      v = kwargs.pop('index')
      self.index = tuple(v) if isinstance(v, list) else v
    if 'index2' in kwargs:
      v = kwargs.pop('index2')
      self.index2 = tuple(v) if isinstance(v, list) else v
    self.reset()
    super().__init__(**kwargs)

  def reset(self):
    self.bins = np.zeros(self.nbins)
    self.overflow = 0.0
    self.underflow = 0.0
    self.sum = 0.0
    self.sum2 = 0.0
    self.count = 0
    self.changed = True

  def fill(self, data):
    if self.index != None:
      if self.index2 != None:
        x = data[self.field][self.index][self.index2]
      else:
        x = data[self.field][self.index]
    else:
      x = data[self.field]
    ix = int(self.nbins * (x - self.xlow) / (self.xhigh - self.xlow))
    if ix < 0:
      self.underflow += 1.0
    elif ix >= self.nbins:
      self.overflow += 1.0
    else:
      self.bins[ix] += 1.0
    self.sum += x
    self.sum2 += x*x
    self.count += 1
    self.changed = True

  def summary(self):
    return {
             'name': self.name,
             'nbins': self.nbins,
             'xlow': self.xlow,
             'xhigh': self.xhigh,
             'field': self.field,
             'index': self.index,
             'index2': self.index2,
             'underflow': self.underflow,
             'overflow': self.overflow,
             'sum': self.sum,
             'sum2': self.sum2,
             'count': self.count,
             'bins': self.bins,
           }

  def mean(self):
    return self.sum / self.count

  def variance(self):
    x = self.sum / self.count
    xx = self.sum2 / self.count
    return xx - x*x

  def update(self, data):
    action = data['action']
    if action == 'alert':
      self.fill(data)
    elif action == 'reset':
      self.reset()
    elif action == 'report':
      if self.changed: # only if there has been a change since last report
        data.update(self.summary())
        self.changed = False
        self.notify(action, None, data)

