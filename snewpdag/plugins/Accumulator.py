"""
Accumulator:  a plugin which simply accumulates a list of numbers
  Only forwards reports downstream.
"""
import logging

from snewpdag.dag import Node

class Accumulator(Node):
  def __init__(self, title, field, **kwargs):
    self.title = title
    self.field = field
    self.index = None
    if 'index' in kwargs:
      self.index = kwargs.pop('index')
    self.reset()
    super().__init__(**kwargs)

  def reset(self):
    self.series = []

  def fill(self, data):
    if self.index:
      x = data[self.field][self.index]
    else:
      x = data[self.field]
    self.series.append(x)

  def summary(self):
    return {
             'name': self.name,
             'title': self.title,
             'field': self.field,
             'index': self.index,
             'series': self.series,
           }

  def update(self, data):
    action = data['action']
    if action == 'alert':
      self.fill(data)
    elif action == 'reset':
      self.reset()
    elif action == 'report':
      data['histogram'] = self.summary()
      self.notify(action, None, data)

