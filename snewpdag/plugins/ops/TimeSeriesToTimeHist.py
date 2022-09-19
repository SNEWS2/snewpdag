"""
TimeSeriesToTimeHist - use a TSeries to fill a THist.
  Reference time (defining t=0) is kept the same.

Arguments:
  in_field:  input field name
  out_field:  output field name
  start:  float or (s,ns) to indicate start time
  duration:  duration of histogram in seconds
  nbins:  number of bins
"""
import logging
import numpy as np
from astropy import units as u

from snewpdag.dag import Node
from snewpdag.dag.lib import field2ns
from snewpdag.values import THist, TSeries

class TimeSeriesToTimeHist(Node):
  def __init__(self, in_field, out_field, start, duration, nbins, **kwargs):
    self.in_field = in_field
    self.out_field = out_field
    self.start = field2ns(start)
    self.duration = duration
    self.nbins = nbins
    super().__init__(**kwargs)

  def alert(self, data):
    if self.in_field in data:
      ts = data[self.in_field]
      if isinstance(ts, TimeSeries):
        th = THist(ts.reference, self.nbins, self.start,
                   self.start + self.duration * ns_per_second)
        th.add_offsets(ts.offsets, unit=u.ns)
        data[self.out_field] = th
        return data
    return False

