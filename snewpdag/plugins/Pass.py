"""
Pass - a pass-through node

Configuration parameters:
  'line':  print a line every n events.  0 if no print.  Default 100.
  'dump':  dump data dictionary every n events.  0 if no print.  Default 0.
"""
import logging

from snewpdag.dag import Node

class Pass(Node):
  def __init__(self, **kwargs):
    self.line = 100
    self.dump = 0
    if 'line' in kwargs:
      self.line = kwargs['line']
      kwargs.pop('line')
    if 'dump' in kwargs:
      self.dump = kwargs['dump']
      kwargs.pop('dump')
    self.count = 0
    super().__init__(**kwargs)

  def print_dict(self, indent, data):
    for k, v in data.items():
      if isinstance(v, dict):
        print('{0}{1}:'.format(indent, k))
        self.print_dict(indent + '  ', v)
      else:
        print('{0}{1}: {2}'.format(indent, k, v))

  def update(self, data):
    self.count += 1
    if self.line > 0:
      if self.count == 1 or self.count % self.line == 0:
        if 'action' in data:
          print('{0} received {1} messages (action {2})'.format(
                self.name, self.count, data['action']))
        else:
          logging.error('{0} received {1} messages'.format(
                        self.name, self.count))
    if self.dump > 0:
      if self.count == 1 or self.count % self.dump == 0:
        print('**** {0} **** ({1})'.format(self.name, self.count))
        self.print_dict('', data)
        print('---- {} ----'.format(self.name))
    self.notify(data['action'], None, data)

