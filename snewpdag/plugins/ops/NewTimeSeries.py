"""
NewTimeSeries - initialize an empty TimeSeries object

Arguments:
  out_field:  output field name
  start:  float or (s,ns) or UTC string to indicate start time
  reference (optional):  float or (s,ns) to indicate what t=0 refers to
  duration:  duration in seconds (0 if indeterminate)

"start" is really more like a reference time for the time series,
since it can contain negative values.

Valid time formats:
  float - time in seconds in Unix epoch
  (n, ns) - Unix epoch
  string - UTC time string
  (string, ns) - UTC time string for seconds, nanoseconds field
"""
import logging
import numpy as np
import numbers

from snewpdag.dag import Node
from snewpdag.dag.lib import time_tuple_from_field
from snewpdag.values import TimeSeries

class NewTimeSeries(Node):
  def __init__(self, out_field, start, **kwargs):
    self.out_field = out_field
    self.start = time_tuple_from_field(start)
    reft = kwargs.pop('reference', start)
    self.reference = time_tuple_from_field(reft)
    self.duration = kwargs.pop('duration', 0)
    super().__init__(**kwargs)

  def alert(self, data):
    data[self.out_field] = TimeSeries(self.start, self.duration,
                                      reference=self.reference)
    return data

