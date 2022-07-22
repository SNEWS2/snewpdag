"""
NewTimeSeries - initialize an empty TimeSeries object

Arguments:
  out_field:  output field name
  start:  float or (s,ns) to indicate start time
  duration:  duration in seconds (0 if indeterminate)
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.values import TimeSeries

class NewTimeSeries(Node):
  def __init__(self, out_field, start, **kwargs):
    self.out_field = out_field
    if np.isscalar(start):
      self.start = time_tuple_from_float(start)
    else:
      self.start = np.array(start)
    self.duration = kwargs.pop('duration', 0)
    super().__init__(**kwargs)

  def alert(self, data):
    data[self.out_field] = TimeSeries(self.start, self.duration)
    return data

