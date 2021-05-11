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
  flags: list of strings. Default is off for all flags.
    accumulate - accumulate over alerts, clear after report

Output json:
  alert:  no output
  reset:  no output
  revoke:  no output
  report:  add the following
    name
    nbins, xlow, xhigh
    field, index, index2
    underflow, overflow
    sum, sum2
    count
    bins
    (doesn't delete input field, since it's not much data
    and may be part of an aggregate)
"""
import sys
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
    self.accumulate = False
    if 'index' in kwargs:
      v = kwargs.pop('index')
      self.index = tuple(v) if isinstance(v, list) else v
    if 'index2' in kwargs:
      v = kwargs.pop('index2')
      self.index2 = tuple(v) if isinstance(v, list) else v
    if 'flags' in kwargs:
      flags = kwargs.pop('flags')
      self.accumulate = 'accumulate' in flags
    self.clear()
    super().__init__(**kwargs)

  def clear(self):
    self.bins = np.zeros(self.nbins)
    self.overflow = 0.0
    self.underflow = 0.0
    self.sum = 0.0
    self.sum2 = 0.0
    self.count = 0
    self.changed = True

  def fill(self, data):
    if self.field in data:
      if self.index != None:
        if isinstance(self.index, int) or self.index in data[self.field]:
          if self.index2 != None:
            if isinstance(self.index2, int) or self.index2 in data[self.field][self.index]:
              x = data[self.field][self.index][self.index2]
            else:
              logging.info('{0}: index2 {1} not found in data'.format(
                           self.name, self.index2))
              logging.info('data = {}'.format(data[self.field][self.index]))
              return
          else:
            x = data[self.field][self.index]
        else:
          logging.info('{0}: index {1} not found in data'.format(
                       self.name, self.index))
          return
      else:
        x = data[self.field]
    else:
      # field not in data
      logging.info('{0}: field {1} not found in data'.format(self.name, self.field))
      return

    try:
      # need to protect against invalid values
      #logging.info('Received in {0}: {1}'.format(self.name, x))
      #logging.info('Indices {} / {} / {}'.format(self.field, self.index, self.index2))
      ix = int(self.nbins * (x - self.xlow) / (self.xhigh - self.xlow))
    except:
      logging.info('Calculation error in {0}: {1}'.format(self.name, sys.exc_info()))
      return

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

  def alert(self, data):
    self.fill(data)
    return False # don't forward an alert

  def reset(self, data):
    return False

  def revoke(self, data):
    return False

  def report(self, data):
    if self.changed:
      data.update(self.summary())
      self.changed = False
      return True
    else:
      return False # or else will duplicate same plot for same report

