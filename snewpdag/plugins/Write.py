"""
Write - write fields into the payload

configuration:
  on: list of 'alert', 'revoke', 'report', 'reset' (optional: def 'alert' only)
  write: ( (field,value), ... )

Field names take the form of dir1/dir2/dir3,
which in the payload will be data[dir1][dir2][dir3]
"""
import logging

from snewpdag.dag import Node

class Write(Node):
  def __init__(self, write, **kwargs):
    self.writes = []
    for op in write:
      dst = op[0].split('/')
      self.writes.append( [dst[:-1], dst[-1], op[1]] )
    self.on = kwargs.pop('on', [ 'alert' ])
    super().__init__(**kwargs)

  def ops(self, data):
    for op in self.writes:
      d = data
      for k in op[0]:
        if k not in d:
          d[k] = {}
        d = d[k]
      d[op[1]] = op[2]
    return data

  def alert(self, data):
    return self.ops(data) if 'alert' in self.on else True

  def revoke(self, data):
    return self.ops(data) if 'revoke' in self.on else True

  def reset(self, data):
    return self.ops(data) if 'reset' in self.on else True

  def report(self, data):
    return self.ops(data) if 'report' in self.on else True

