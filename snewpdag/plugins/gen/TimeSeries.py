"""
TimeSeries:  generates a time series on each alert, based on a histogram

(Should we use a kernel density estimator instead?)

configuration:
  sig_mean:  mean number of events to be generated for each alert.

output added to data:
  'times': times of individual events based on histogram.
           Use uniform distribution within a bin.
           Note that the array is not sorted.
"""
import logging
import numpy as np
import matplotlib.pyplot as plt
from snewpdag.dag import Node
from . import TimeDistSource

class TimeSeries(TimeDistSource):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    area = sum(self.mu)
    # Define mean (total number of signal events) as the integral of the lightcurve model
    #print(self.mu)
    self.mean = area # Factor of 10 needed to recover correct nevents after the generator
    # normalize histogram to unit area
    self.nmu = self.mu / area
    self.nmu.flags.writeable = False
    # append self.thi (high end) to t array
    self.tedges = np.append(self.t, self.thi)
    #print('Trial:', len(self.mu), self.name)
    #exit()

  def alert(self, data):
    tdelay = data['sig_t_delay'] if 'sig_t_delay' in data else 0
    nev = Node.rng.poisson(self.mean)
    size = len(self.mu)
    j = Node.rng.choice(size, nev, p=self.nmu, replace=True, shuffle=False)
    t0 = self.tedges[j]
    dt = self.tedges[j+1] - t0
    a = Node.rng.random(nev) * dt + t0 + tdelay
    a.flags.writeable = False

    ngen = { 'times': a, 'gen_t_delay': tdelay }
    if 'gen' in data:
      data['gen'] += (ngen, )
    else:
      data['gen'] = (ngen, )

    #if 'sig_times' in data:
    #  data['sig_times'] = np.concatenate(data['sig_times'], a) # immutability issue?
    #  print('I am here')
    #else:
    #  data['sig_times'] = a
    #  print('or here')
    #print('lets see', nev, len(data['times']), self.name)
    #plt.hist(data['times'])
    #plt.show()
    return True

