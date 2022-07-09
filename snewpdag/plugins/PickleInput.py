"""
PickleInput
Configuration options:
  on:  list of 'alert', 'report', 'revoke', 'reset' (default 'report')
  filename:  input filename
"""
import logging
import pickle

from snewpdag.dag import Node

class PickleInput(Node):
  def __init__(self, filename, **kwargs):
    self.filename = filename
    self.on = kwargs.pop('on', [ 'report' ])
    super().__init__(**kwargs)

  def ops(self, data):
    """
    load pickle, but keep the following payload fields:  action, name, history
    """
    with open(self.filename, 'rb') as f:
      d = pickle.load(f)
    for k, v in d.items():
      if k not in ('action', 'name', 'history'):
        data[k] = v # shallow copy, which should be fine here
    return data

  def alert(self, data):
    return self.ops(data) if 'alert' in self.on else False

  def revoke(self, data):
    return self.ops(data) if 'revoke' in self.on else True

  def reset(self, data):
    return self.ops(data) if 'reset' in self.on else True

  def report(self, data):
    return self.ops(data) if 'report' in self.on else False

