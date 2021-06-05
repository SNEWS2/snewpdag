"""
History - a history object. Mostly for defining operations.
"""
import logging

class History:
  def __init__(self):
    self.val = []

  def clear(self):
    self.val = []

  # append a string to the history
  def append(self, item):
    self.val.append(item)

  # replace history with a single item which is a list of History objects
  def combine(self, hists):
    self.val = [ tuple( h.emit() for h in hists ) ]

  # emit as a tuple
  def emit(self):
    t = tuple( tuple(v) if isinstance(v, list) else v for v in self.val )
    return t

