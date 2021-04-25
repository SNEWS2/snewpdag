"""
TimeDist:  generates a time distribution on each alert, based on a histogram

configuration:
  seed:  random number seed (integer)
  mean:  normalization.  Histogram normalized to this area before generations.
         (This means generated histogram will vary in area)

output added to data:
  't': low edges of time bins (array of floats)
  'n': number of events in corresponding time bins (array of floats)

Originally based on Vladimir's TimeDistFileInput
"""
import logging
import numpy as np

from . import TimeDistSource

class TimeDist(TimeDistSource):

  def __init__(self, mean, seed, **kwargs):
    self.rng = np.random.default_rng(seed)
    super().__init__(**kwargs)
    # normalize to specified mean
    area = sum(self.mu)
    self.mu = self.mu * mean / area

  def alert(self, data):
    data['t'] = self.t.copy() # or can we just copy a read-only object?
    data['n'] = self.rng.poisson(self.mu, len(self.mu))
    return True

