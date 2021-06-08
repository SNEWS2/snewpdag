"""
History - a history object. Mostly for defining operations.
"""
import logging

class History:
  def __init__(self, val = []):
    self.val = list(val)

  def copy(self):
    o = History()
    o.val = self.val.copy()
    return o

  def clear(self):
    self.val = []

  # append a string to the history
  def append(self, item):
    self.val.append(item)

  # replace history with a single item which is a list of History objects
  def combine(self, hists):
    v = [ tuple( h.emit() for h in hists ) ]
    self.val = v

  # emit as a tuple
  def emit(self):
    t = tuple( tuple(v) if isinstance(v, list) else v for v in self.val )
    return t

  def last(self):
    if len(self.val) > 0:
      return self.val[-1]
    else:
      return None

  def __str__(self):
    return str(self.emit())

