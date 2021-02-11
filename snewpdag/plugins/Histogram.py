"""
Histogram:  a plugin which accumulates a histogram based on its configuration

Constructor arguments:
  title: string, histogram title
  nbins: number of bins
  xlow: low edge of histogram
  xhigh: high edge of histogram
  field: string, name of field to extract from alert data
  index: int or tuple, element numbers if field is an array

(Could also specify variable-width bins?)
"""
import logging
import numpy as np

from snewpdag.dag import Node

class Histogram(Node):
  def __init__(self, title, nbins, xlow, xhigh, field, **kwargs):
    self.title = title
    self.nbins = nbins
    self.xlow = xlow
    self.xhigh = xhigh
    self.field = field
    self.index = None
    if 'index' in kwargs:
      self.index = kwargs.pop('index')
    self.reset()
    super().__init__(**kwargs)

  def reset(self):
    self.bins = np.zeros(self.nbins)
    self.overflow = 0.0
    self.underflow = 0.0
    self.sum = 0.0
    self.sum2 = 0.0
    self.count = 0

  def fill(self, data):
    if self.index:
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

  def summary(self):
    return {
             'name': self.name,
             'title': self.title,
             'nbins': self.nbins,
             'xlow': self.xlow,
             'xhigh': self.xhigh,
             'field': self.field,
             'index': self.index,
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
      data['histogram'] = self.summary()
    self.notify(action, None, data)


