"""
NewTimeHist - initialize an empty TimeHist object

Arguments:
  out_field:  output field name
  start_time:  float or (s,ns) to indicate start time
  time_span:  duration of histogram in seconds
  nbins:  number of bins
"""
import logging

from snewpdag.dag import Node
from snewpdag.values import TimeHist

class NewTimeHist(Node):
  def __init__(self, out_field, start_time):
    self.out_field = out_field
    if np.isscalar(start_time):
      self.start = time_tuple_from_float(start_time)
    else:
      self.start = np.array(start_time)
    self.time_span = time_span
    self.nbins = nbins
    super().__init__(**kwargs)

  def alert(self, data):
    data[self.out_field] = TimeHist(self.start, self.time_span, self.nbins)
    return data

