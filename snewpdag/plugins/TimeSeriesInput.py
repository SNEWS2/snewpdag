"""
TimeSeriesInput:  plugin which takes time series data.

This just validates that, if the data is an alert, it has a 'times'
field to store an array of times.

If the data is a revocation, no such check is performed.

We might want to check that 'times' contains an array of numbers.
At this point we don't.

It is not assumed that the time data is sorted.
"""
import logging

from snewpdag.dag import Node

class TimeSeriesInput(Node):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)

  def alert(self, data):
    """
    Check that the input has the right fields:
    - if it's an alert, it should have a times field.
    - if it's not an alert, just pass it along.
    """
    if 'times' in data:
      return True
    else:
      logging.error('[{}] Expected times field not found'.format(self.name))
      return False

