"""
WriteField - write fields into the payload.
  based on Write, but using a tuple to specify the target

arguments:
  on: list of 'alert', 'revoke', 'report', 'reset' (optional: def 'alert' only)
  write: ( (fieldspec, value), ... )

fieldspec is a tuple (field, subfield, subsubfield, ...)
"""
import logging

from snewpdag.dag import Node

class WriteField(Node):
  def __init__(self, write, **kwargs):
    self.writes = write
    self.on = kwargs.pop('on', [ 'alert' ])
    super().__init__(**kwargs)

  def ops(self, data):
    for op in self.writes:
      fields = op[0]
      d = data
      for f in fields[:-1]:
        if isinstance(d, dict) and f in d:
          d = d[f]
        else:
          d[f] = {}
          d = d[f]
      d[fields[-1]] = op[1]
    return data

  def alert(self, data):
    return self.ops(data) if 'alert' in self.on else True

  def revoke(self, data):
    return self.ops(data) if 'revoke' in self.on else True

  def reset(self, data):
    return self.ops(data) if 'reset' in self.on else True

  def report(self, data):
    return self.ops(data) if 'report' in self.on else True

