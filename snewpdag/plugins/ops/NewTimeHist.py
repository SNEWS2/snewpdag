"""
NewTimeHist - initialize an empty THist object

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
from snewpdag.dag.lib import field2ns, ns_per_second
from snewpdag.values import THist

class NewTimeHist(Node):
  def __init__(self, out_field, start, duration, nbins, **kwargs):
    self.out_field = out_field
    self.start = field2ns(start)
    reft = kwargs.pop('reference', start)
    self.reference = field2ns(reft)
    self.duration = duration
    self.nbins = nbins
    super().__init__(**kwargs)

  def alert(self, data):
    data[self.out_field] = THist(self.reference, self.nbins, self.start,
                                 self.start + self.duration * ns_per_second)
    return data

