"""
CopyField - copy fields within the payload.
  like Copy, but using tuples as field specifiers

arguments:
  on: list of 'alert', 'revoke', 'report', 'reset' (optional: def 'alert' only)
  copy: ( (from, to), ... )

from and to are tuples (field, subfield, subsubfield, ...)
"""
import logging

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field, store_field

class CopyField(Node):
  def __init__(self, copy, **kwargs):
    self.copies = copy
    self.on = kwargs.pop('on', [ 'alert' ])
    super().__init__(**kwargs)

  def ops(self, data):
    for op in self.copies:
      v, exist = fetch_field(data, op[0])
      if exist:
        store_field(data, op[1], v)
      else:
        logging.error('{}: field {} not found'.format(self.name, op[0]))
    return data

  def alert(self, data):
    return self.ops(data) if 'alert' in self.on else True

  def revoke(self, data):
    return self.ops(data) if 'revoke' in self.on else True

  def reset(self, data):
    return self.ops(data) if 'reset' in self.on else True

  def report(self, data):
    return self.ops(data) if 'report' in self.on else True

