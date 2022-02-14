"""
GenerateSGBG

Lightcurve generator: simulates a random time delay for the signal at a given distance as well as a poisson background on top of it

configuration:
  dist: distance to the source in [kpc] (default: 10)
  sig_mean:  expected mean for the experiment in 6s for a source at 10kpc (default: sum of input array)
  bg: expected background of the experiment
  detector: detector name

output added to data:
  'times': times of individual events based on histogram.
           Use uniform distribution within a bin.
           Note that the array is not sorted.

Author: M. Colomer (marta.colomer@ulb.be)
"""
import logging
from statistics import mean
import numpy as np
import matplotlib.pyplot as plt
from snewpdag.dag import Node
from . import TimeDistSource

class Generate_delta_peak(Node):

  def __init__(self, detector, mean, bg, **kwargs):
    #logging.info("GenerateSGBG: dist {} bg {}".format(dist, bg))
    super().__init__(**kwargs)
    self.bg = bg #mean number of events per ms bin
    self.detector = detector
    self.dist = kwargs.pop('dist', 10)
    self.mean = mean #mean number of events per ms bin
    self.tmin = -10
    self.tmax = 10
    self.tstart = int(Node.rng.uniform(-2, 2)) #random tstart between -2 and 2 sec
    self.duration = int(Node.rng.uniform(0.2, 0.8)) #random weight of peak between [200 and 800 ms]
    
  def alert(self, data):
    
    #logging.info('times are {}'.format(self.t[-1]))
    new_times = np.arange(self.tmin,self.tmax,0.001)
    #self.tdelay = int(Node.rng.uniform(-20.0, 20.0))

    #logging.info('t_true {}'.format(t_true))
    new_data = []
    t_true = self.tstart/1000.
    dist = data['sn_distance'] if 'sn_distance' in data else self.dist

    #Construct new data with tdelay and sg + bg
    for i,ti in enumerate(new_times):
      #when only background
      bg = self.bg
      #during delta peak
      if ti>=self.tstart and ti<self.tstart + self.duration:
        signal = self.mean 
        new_data.append(signal+bg)
      else:
        new_data.append(bg)

    #randomise the lightcurve    
    tarea = sum(new_data)
    new_mu = np.array(new_data) / tarea # normalize histogram to unit area
    nev = Node.rng.poisson(tarea)
    size = len(new_data)
    j = Node.rng.choice(size, nev, p=new_mu, replace=True, shuffle=False)
    t0 = new_times[j-1]
    dt = new_times[j] - t0

    a = Node.rng.random(nev) * dt + t0
    a.flags.writeable = False
    
    ngen = { 'times': a, 't_true': t_true }
    if 'gen' in data:
      data['gen'] += (ngen, )
    else:
      data['gen'] = (ngen, )

    data['detector_name'] = self.detector 

    return True

