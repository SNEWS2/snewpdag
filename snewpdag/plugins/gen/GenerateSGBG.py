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
from statistics import mean
import numpy as np
import matplotlib.pyplot as plt
from . import TimeDistSource

class GenerateSGBG(TimeDistSource):

  def __init__(self, mean, seed, bg, **kwargs):
    self.mean = mean
    print(mean, seed, bg)
    self.bg = bg
    self.rng = np.random.default_rng(seed)
    super().__init__(**kwargs)
    self.tmin = -10
    self.tmax = 10
    self.tdelay = int(np.random.uniform(-20,20))
    
  def update(self, data):
    action = data['action']
    if action == 'alert':
      print('times are', self.t[-1])
      new_times = np.arange(self.tmin,self.tmax,0.001)
      t_true = self.tdelay
      print(t_true)
      new_data = []

      #Construct new data with tdelay and sg+bg
      for i,ti in enumerate(new_times):
        bg = self.bg
        if ti>=t_true/1000. and ti<self.t[-1]-0.001+t_true/1000.:                                                                                   
          signal = self.mu[i-t_true+self.tmin*1000-1]
          new_data.append(signal+bg)
        else:
          new_data.append(bg)

      #randomise the lightcurve    
      tarea = sum(new_data)                                                                                                                                        
      new_mu = np.array(new_data) / tarea 
      nev = self.rng.poisson(tarea)
      size = len(new_data)
      j = self.rng.choice(size, nev, p=new_mu, replace=True, shuffle=False)
      t0 = new_times[j-1]
      dt = new_times[j] - t0
      data['times'] = self.rng.random(nev) * dt + t0

    self.notify(action, None, data)

