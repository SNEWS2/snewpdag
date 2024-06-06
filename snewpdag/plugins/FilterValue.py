"""
FilterValue - check that a payload key gives a certain value.
If not, consume the action.

Constructor arguments:
  in_field: string, name of field to check
  value: value to check against
  on_alert, on_reset, on_revoke, on_report: boolean, optional,
    run check on these actions, else pass through (return True)
"""
import logging

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field

class FilterValue(Node):
  def __init__(self, in_field, value, **kwargs):
    self.in_field = in_field
    self.value = value
    on_list = kwargs.pop('on', ['alert'])
    self.on_alert = kwargs.pop('on_alert', 'alert' in on_list)
    self.on_reset = kwargs.pop('on_reset', 'reset' in on_list)
    self.on_revoke = kwargs.pop('on_revoke', 'revoke' in on_list)
    self.on_report = kwargs.pop('on_report', 'report' in on_list)
    op = kwargs.pop('op', '=')
    self.eq = op in ['=', '>=', '<=', 'eq', 'ge', 'le']
    self.gt = op in ['>', '>=', 'gt', 'ge']
    self.lt = op in ['<', '<=', 'lt', 'le']
    super().__init__(**kwargs)

  def check_value(self, data):
    v, valid = fetch_field(data, self.in_field)
    if not valid:
      return False
    return (self.gt and v > self.value) or \
           (self.lt and v < self.value) or \
           (self.eq and v == self.value)

  def alert(self, data):
    return self.check_value(data) if self.on_alert else True

  def revoke(self, data):
    return self.check_value(data) if self.on_revoke else True

  def reset(self, data):
    return self.check_value(data) if self.on_reset else True

  def report(self, data):
    return self.check_value(data) if self.on_report else True

