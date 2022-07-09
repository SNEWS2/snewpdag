"""
TimeSeriesToTimeHist - use a TimeSeries to fill a TimeHist

Arguments:
  in_field:  input field name
  out_field:  output field name
  start_time:  float or (s,ns) to indicate start time
  time_span:  duration of histogram in seconds
  nbins:  number of bins
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.values import TimeHist, TimeSeries

class TimeSeriesToTimeHist(Node):
  def __init__(self, in_field, out_field, start_time, time_span, nbins, **kwargs):
    self.in_field = in_field
    self.out_field = out_field
    self.start = time_tuple_from_float(start_time) if np.isscalar(start_time) \
                 else np.array(start_time)
    self.time_span = time_span
    self.nbins = nbins
    super().__init__(**kwargs)

  def alert(self, data):
    if self.in_field in data:
      ts = data[self.in_field]
      if isinstance(ts, TimeSeries):
        th = TimeHist(self.start, self.time_span, self.nbins)
        th.add_offsets(ts.times)
        data[self.out_field] = th
        return data
    return False

