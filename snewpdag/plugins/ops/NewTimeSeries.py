"""
NewTimeSeries - initialize an empty TimeSeries object

Arguments:
  out_field:  output field name
  start_time:  float or (s,ns) to indicate start time
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.values import TimeSeries

class NewTimeSeries(Node):
  def __init__(self, out_field, start_time, **kwargs):
    self.out_field = out_field
    if np.isscalar(start_time):
      self.start = time_tuple_from_float(start_time)
    else:
      self.start = np.array(start_time)
    super().__init__(**kwargs)

  def alert(self, data):
    data[self.out_field] = TimeSeries(self.start)
    return data

