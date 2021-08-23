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

class FilterValue(Node):
  def __init__(self, in_field, value, **kwargs):
    self.in_field = in_field
    self.value = value
    self.on_alert = kwargs.pop('on_alert', True)
    self.on_reset = kwargs.pop('on_reset', False)
    self.on_revoke = kwargs.pop('on_revoke', False)
    self.on_report = kwargs.pop('on_report', False)
    super().__init__(**kwargs)

  def check_value(self, data):
    if self.in_field in data:
      return data[self.in_field] == self.value
    else:
      return False

  def alert(self, data):
    return self.check_value(data) if self.on_alert else True

  def revoke(self, data):
    return self.check_value(data) if self.on_revoke else True

  def reset(self, data):
    return self.check_value(data) if self.on_reset else True

  def report(self, data):
    return self.check_value(data) if self.on_report else True

