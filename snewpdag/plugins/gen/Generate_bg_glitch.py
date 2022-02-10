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

class Generate_bg_glitch(TimeDistSource):

  def __init__(self, bg, detector, **kwargs):
    #logging.info("GenerateSGBG: dist {} bg {}".format(dist, bg))
    super().__init__(**kwargs)
    self.bg = bg
    self.detector = detector
    self.dist = kwargs.pop('dist', 10)
    area = sum(self.mu)
    self.mean = kwargs.pop('sig_mean', area)
    self.new_mu = self.mu*self.mean/area
    self.tmin = -10
    self.tmax = 10
    self.tdelay = 0 #maybe put as input field?
    self.glitch_tstart = 0.5 #maybe put as input field?
    self.glitch_duration = 0.1 #maybe put as input field?
    self.glitch_amplitude = 2 #maybe put as input field?
    print(self.mean, area)
    
  def alert(self, data):
    
    #logging.info('times are {}'.format(self.t[-1]))
    new_times = np.arange(self.tmin,self.tmax,0.001)
    #self.tdelay = int(Node.rng.uniform(-20.0, 20.0))

    t_true = self.tdelay
    #logging.info('t_true {}'.format(t_true))
    new_data = []

    dist = data['sn_distance'] if 'sn_distance' in data else self.dist

    #Construct new data with tdelay and sg + bg
    for i,ti in enumerate(new_times):
      #bg when no glitch
      bg = self.bg
      #bg during glicth
      if ti>=self.glitch_tstart and ti<self.glitch_tstart + self.glitch_duration:
        bg = self.bg*self.glitch_amplitude
        
      #in signal region
      if ti>=t_true/1000. and ti<self.t[-1]-0.001+t_true/1000.:                                                                                   
        signal = self.new_mu[i-t_true+self.tmin*1000-1]*(10./dist)**2
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

