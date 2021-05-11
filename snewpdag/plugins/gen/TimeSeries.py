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
import matplotlib.pyplot as plt
from . import TimeDistSource

class TimeSeries(TimeDistSource):

  def __init__(self, seed, **kwargs):
    self.rng = np.random.default_rng(seed)
    super().__init__(**kwargs)
    area = sum(self.mu)
    # Define mean (total number of signal events) as the integral of the lightcurve model
    print(self.mu)
    self.mean = area # Factor of 10 needed to recover correct nevents after the generator
    # normalize histogram to unit area
    self.mu = self.mu / area
    #print('Trial:', len(self.mu), self.name)
    #exit()
  def alert(self, data):
    tdelay = data['tdelay'] if 'tdelay' in data else 0
    nev = self.rng.poisson(self.mean)
    size = len(self.mu)
    j = self.rng.choice(size, nev, p=self.mu, replace=True, shuffle=False)
    t0 = self.t[j]
    dt = self.t[j+1] - t0
    a = self.rng.random(nev) * dt + t0 + tdelay
    if 'times' in data:
      data['times'] = np.concatenate(data['times'], a)
      print('I am here')
    else:
      data['times'] = a
      print('or here')
    print('lets see', nev, len(data['times']), self.name)
    #plt.hist(data['times'])
    #plt.show()
    return True

