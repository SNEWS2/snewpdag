"""
TimeSeries:  generates a time series on each alert, based on a histogram

(Should we use a kernel density estimator instead?)

configuration:
  mean:  mean number of events to be generated for each alert.
  seed:  random number seed (integer)

output added to data:
  'times': times of individual events based on histogram.
           Use uniform distribution within a bin.
           Note that the array is not sorted.
"""
import logging
import numpy as np

from . import TimeDistSource

class TimeSeries(TimeDistSource):

  def __init__(self, mean, seed, **kwargs):
    self.mean = mean
    self.rng = np.random.default_rng(seed)
    super().__init__(**kwargs)
    # normalize histogram to unit area
    area = sum(self.mu)
    self.mu = self.mu / area

  def update(self, data):
    action = data['action']
    if action == 'alert':
      nev = self.rng.poisson(self.mean)
      size = len(self.mu)
      j = self.rng.choice(size, nev, p=self.mu, replace=True, shuffle=False)
      t0 = self.t[j]
      dt = self.t[j+1] - t0
      data['times'] = self.rng.random(nev) * dt + t0
    self.notify(action, None, data)

