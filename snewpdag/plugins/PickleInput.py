"""
PickleInput
Configuration options:
  filename:  input filename
"""
import logging
import pickle

from snewpdag.dag import Node

class PickleInput(Node):
  def __init__(self, filename, **kwargs):
    self.filename = filename
    super().__init__(**kwargs)

  def alert(self, data):
    """
    load pickle, but keep the following payload fields:  action, name, history
    """
    with open(self.filename, 'rb') as f:
      d = pickle.load(f)
    for k, v in d.items():
      if k not in ('action', 'name', 'history'):
        data[k] = v # shallow copy, which should be fine here
    return data

