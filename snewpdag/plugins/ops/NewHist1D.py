"""
NewTimeHist - initialize an empty TimeHist object

Arguments:
  out_field:  output field name
  start:  float or (s,ns) to indicate start time
  reference (optional):  float or (s,ns) to indicate what t=0 refers to
  duration:  duration of histogram in seconds
  nbins:  number of bins
  reference
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import time_tuple_from_field
from snewpdag.values import TimeHist

class NewTimeHist(Node):
  def __init__(self, out_field, start, duration, nbins, **kwargs):
    self.out_field = out_field
    self.start = time_tuple_from_field(start)
    reft = kwargs.pop('reference', start)
    self.reference = time_tuple_from_field(reft)
    self.duration = duration
    self.nbins = nbins
    super().__init__(**kwargs)

  def alert(self, data):
    data[self.out_field] = TimeHist(self.start, self.duration, self.nbins,
                                    reference=self.reference)
    return data

