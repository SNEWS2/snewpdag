"""
Pass - a pass-through node

Configuration parameters:
  'line':  print a line every n events.  0 if no print.  Default 100.
  'dump':  dump data dictionary every n events.  0 if no print.  Default 0.

Output json:
  input json passed on unmodified
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

  def alert(self, data):
    self.count += 1
    if self.line > 0:
      if self.count == 1 or self.count % self.line == 0:
        print('{0}: received {1} alerts'.format(self.name, self.count))
    if self.dump > 0:
      if self.count == 1 or self.count % self.dump == 0:
        print('**** {0} **** ({1}) alert'.format(self.name, self.count))
        self.print_dict('', data)
        print('---- {} ----'.format(self.name))
    return True

  def revoke(self, data):
    if self.dump > 0:
      print('**** {0} **** ({1}) revoke'.format(self.name, self.count))
      self.print_dict('', data)
      print('---- {} ----'.format(self.name))
    return True

  def report(self, data):
    print('**** {0} **** ({1}) report'.format(self.name, self.count))
    self.print_dict('', data)
    print('---- {} ----'.format(self.name))
    return True

  def reset(self, data):
    if self.dump > 0:
      print('**** {0} **** ({1}) reset'.format(self.name, self.count))
      self.print_dict('', data)
      print('---- {} ----'.format(self.name))
    return True

