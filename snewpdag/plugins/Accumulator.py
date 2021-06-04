"""
Accumulator:  a plugin which simply accumulates a list of numbers
  Only forwards reports downstream.

In general, assumes only a single source, so revoke and reset are
the same.
"""
import logging

from snewpdag.dag import Node

class Accumulator(Node):
  def __init__(self, title, in_field, **kwargs):
    self.title = title
    self.in_field = in_field
    self.out_field = kwargs.pop('out_field', None)
    self.index = kwargs.pop('in_index', None)
    super().__init__(**kwargs)
    self.series = []

  def alert(self, data):
    source = data['history'][-1]
    if self.index:
      x = data[self.field][self.index]
    else:
      x = data[self.field]
    # append
    self.series.append(x)
    return False # consume - only emit on report

  def report(self, data):
    a = np.array(self.series)
    a.flags.writeable = False
    d = {
          'name': self.name,
          'title': self.title,
          'in_field': self.field,
          'in_index': self.index,
          'series': a,
        }
    if self.out_field == None:
      data.update(d)
    else:
      data[self.out_field] = d
    return True

  def revoke(self, data):
    self.series = []
    return True

  def reset(self, data):
    self.series = []
    return True

