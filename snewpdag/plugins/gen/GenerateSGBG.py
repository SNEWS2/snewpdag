"""
GenerateSGBG

Lightcurve generator: simulates a random time delay for the signal at a given distance as well as a poisson background on top of it

configuration:
  dist: distance to the source in [kpc]
  bg: expected background of the experiment

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

class GenerateSGBG(TimeDistSource):

  def __init__(self, dist, bg, **kwargs):
    logging.info("GenerateSGBG: dist {} bg {}".format(dist, bg))
    self.bg = bg
    self.dist = dist
    super().__init__(**kwargs)
    self.tmin = -10
    self.tmax = 10
    self.tdelay = -9999
    
  def alert(self, data):
    logging.info('times are {}'.format(self.t[-1]))
    new_times = np.arange(self.tmin,self.tmax,0.001)
    self.tdelay = int(Node.rng.uniform(-20.0, 20.0))

    t_true = self.tdelay
    logging.info('t_true {}'.format(t_true))
    new_data = []

    #Construct new data with tdelay and sg+bg
    for i,ti in enumerate(new_times):
      bg = self.bg
      if ti>=t_true/1000. and ti<self.t[-1]-0.001+t_true/1000.:                                                                                   
        signal = self.mu[i-t_true+self.tmin*1000-1]*(10./self.dist)**2
        new_data.append(signal+bg)
      else:
        new_data.append(bg)

    #randomise the lightcurve    
    tarea = sum(new_data)

    new_mu = np.array(new_data) / tarea 
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

    return True

