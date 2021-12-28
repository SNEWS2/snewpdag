"""
Copy - copy fields into other (possibly new) fields

configuration:
  on: list of 'alert', 'revoke', 'report', 'reset' (optional: def 'alert' only)
  cp: ( (in,out), ... )

Field names take the form of dir1/dir2/dir3,
which in the payload will be data[dir1][dir2][dir3]
"""
import logging

from snewpdag.dag import Node

class Copy(Node):
  def __init__(self, cp, **kwargs):
    self.cp = []
    for op in cp:
      src = op[0].split('/')
      dst = op[1].split('/')
      self.cp.append( [src, dst[:-1], dst[-1]] )
    self.on = kwargs.pop('on', [ 'alert' ])
    super().__init__(**kwargs)

  def copy(self, data):
    for op in self.cp:
      v = data # should just follow references
      for k in op[0]:
        if k in v:
          v = v[k]
        else:
          logging.warning('Field {} not found from source {}'.format(k, op[0]))
          continue
      # v should now hold the value to be copied
      d = data
      for k in op[1]:
        if k not in d:
          d[k] = {}
        d = d[k]
      d[op[2]] = v
    return data

  def alert(self, data):
    return self.copy(data) if 'alert' in self.on else True

  def revoke(self, data):
    return self.copy(data) if 'revoke' in self.on else True

  def reset(self, data):
    return self.copy(data) if 'reset' in self.on else True

  def report(self, data):
    return self.copy(data) if 'report' in self.on else True

