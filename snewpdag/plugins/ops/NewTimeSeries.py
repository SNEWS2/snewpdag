"""
NewTimeSeries - initialize an empty TSeries object

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
from snewpdag.dag.lib import field2ns, ns_per_second
from snewpdag.values import TSeries

class NewTimeSeries(Node):
  def __init__(self, out_field, start, **kwargs):
    self.out_field = out_field
    self.start = field2ns(start)
    reft = kwargs.pop('reference', start)
    self.reference = field2ns(reft)
    self.duration = kwargs.pop('duration', 0)
    super().__init__(**kwargs)

  def alert(self, data):
    data[self.out_field] = TSeries(self.reference, start=self.start,
                                   stop=self.start+self.duration*ns_per_second)
    return data

