"""
NewTimeHist - initialize an empty TimeHist object

Arguments:
  out_field:  output field name
  start:  float or (s,ns) to indicate start time
  duration:  duration of histogram in seconds
  nbins:  number of bins
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.values import TimeHist

class NewTimeHist(Node):
  def __init__(self, out_field, start, duration, nbins, **kwargs):
    self.out_field = out_field
    if np.isscalar(start):
      self.start = time_tuple_from_float(start)
    else:
      self.start = np.array(start)
    self.duration = duration
    self.nbins = nbins
    super().__init__(**kwargs)

  def alert(self, data):
    data[self.out_field] = TimeHist(self.start, self.duration, self.nbins)
    return data

