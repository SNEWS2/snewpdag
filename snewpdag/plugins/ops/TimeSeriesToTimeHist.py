"""
TimeSeriesToTimeHist - use a TimeSeries to fill a TimeHist

Arguments:
  in_field:  input field name
  out_field:  output field name
  start:  float or (s,ns) to indicate start time
  duration:  duration of histogram in seconds
  nbins:  number of bins
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import time_tuple_from_field
from snewpdag.values import TimeHist, TimeSeries

class TimeSeriesToTimeHist(Node):
  def __init__(self, in_field, out_field, start, duration, nbins, **kwargs):
    self.in_field = in_field
    self.out_field = out_field
    self.start = time_tuple_from_field(start)
    self.duration = duration
    self.nbins = nbins
    super().__init__(**kwargs)

  def alert(self, data):
    if self.in_field in data:
      ts = data[self.in_field]
      if isinstance(ts, TimeSeries):
        th = TimeHist(self.start, self.duration, self.nbins)
        th.add_offsets(ts.times)
        data[self.out_field] = th
        return data
    return False

