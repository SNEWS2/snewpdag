"""
PickleOutput
Configuration options:
  filename:  output filename, with fields
             {0} renderer name
             {1} count index, starting from 0
             {2} burst_id from update data (default 0 if no such field)
"""
import logging
import pickle

from snewpdag.dag import Node

class PickleOutput(Node):
  def __init__(self, filename, **kwargs):
    self.filename = filename
    self.count = 0
    super().__init__(**kwargs)

  def write_pickle(self, data):
    burst_id = data.get('burst_id', 0)
    fname = self.filename.format(self.name, self.count, burst_id)
    with open(fname, 'wb') as f:
      pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    return True

  def alert(self, data):
    return self.write_pickle(data)

  def report(self, data):
    return self.write_pickle(data)

