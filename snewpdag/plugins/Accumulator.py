"""
Accumulator:  a plugin which simply accumulates a list of numbers
  Only forwards reports downstream.

In general, assumes only a single source, so revoke and reset are
the same.
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field

class Accumulator(Node):
  def __init__(self, title, in_field, **kwargs):
    self.title = title
    self.in_field = in_field
    self.out_field = kwargs.pop('out_field', None)
    self.index = kwargs.pop('in_index', None)
    self.alert_pass = kwargs.pop('alert_pass', False)
    self.clear_on = kwargs.pop('clear_on', ['revoke','reset'])
    super().__init__(**kwargs)
    self.series = []

  def alert(self, data):
    if self.index:
      x = data[self.in_field][self.index]
    else:
      x, exists = fetch_field(data, self.in_field)
      if not exists:
        return False
    # append
    self.series.append(x)
    return self.alert_pass != False

  def report(self, data):
    a = np.array(self.series)
    a.flags.writeable = False
    d = {
          'name': self.name,
          'title': self.title,
          'in_field': self.in_field,
          'in_index': self.index,
          'series': a,
        }
    if self.out_field == None:
      data.update(d)
    else:
      data[self.out_field] = d
    return True

  def revoke(self, data):
    if 'revoke' in self.clear_on:
      self.series = []
    return True

  def reset(self, data):
    if 'reset' in self.clear_on:
      self.series = []
    return True

