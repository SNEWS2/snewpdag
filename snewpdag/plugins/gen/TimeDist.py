"""
TimeDist:  generates a time distribution on each alert, based on a histogram

configuration:
  sig_mean:  normalization.  Histogram normalized to this area before
             generations.  (This means generated histogram will vary in area)

output added to data:
  't_low': low edges of time bins (array of floats)
  't_high': high edge of last time bins
  't_bins': number of events in corresponding time bins (array of floats)

Originally based on Vladimir's TimeDistFileInput
"""
import logging
import numpy as np

from snewpdag.dag import Node
from . import TimeDistSource

class TimeDist(TimeDistSource):

  def __init__(self, sig_mean, **kwargs):
    super().__init__(**kwargs)
    # normalize to specified mean
    area = sum(self.mu)
    self.nmu = self.mu * (sig_mean / area)
    self.nmu.flags.writeable = False

  def alert(self, data):
    ngen = { 't_low': self.t, # immutable (from TimeDistSource)
             't_high': self.thi, }
    ngen['t_bins'] = Node.rng.poisson(self.nmu, len(self.nmu))
    ngen['t_bins'].flags.writeable = False
    if 'gen' in data:
      data['gen'] += (ngen, )
    else:
      data['gen'] = (ngen, )
    return True

