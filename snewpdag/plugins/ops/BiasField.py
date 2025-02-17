"""
BiasField - add an offset to a field in the payload

arguments:
  on: list of 'alert', 'revoke', 'report', 'reset' (optional: def 'alert' only)
  field: field specifier
  bias: number to add
"""
import logging

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field, store_field

class BiasField(Node):
  def __init__(self, field, bias, **kwargs):
    self.field = field
    self.bias = bias
    self.on = kwargs.pop('on', ['alert'])
    super().__init__(**kwargs)

  def ops(self, data):
    v, exist = fetch_field(data, self.field)
    if exist:
      store_field(data, self.field, v + self.bias)
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

