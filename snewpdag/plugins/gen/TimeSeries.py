"""
TimeSeries:  generates a time series on each alert, based on a histogram

(Should we use a kernel density estimator instead?)

configuration:
  sig_mean:  expected mean for the experiment in 6s for a source at 10kpc (default: sum of input array)
  dist: distance (in kpc) to the source (default: 10); read from payload if preceded by TrueDist generator

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

#rdallava: function used to insert a dictionary into a tuple
def add_dictionary_to_a_tuple(dictionary):
  my_tuple = ()
  my_tuple = list(my_tuple)
  my_tuple.append(dictionary)
  my_tuple = tuple(my_tuple)

  return my_tuple

class TimeSeries(TimeDistSource):

  def __init__(self, detector, **kwargs):
    super().__init__(**kwargs)
    area = sum(self.mu)
    self.mean = kwargs.pop('sig_mean', area)
    self.new_mu = self.mu*self.mean/area
    self.dist = kwargs.pop('dist', 10)

    # append self.thi (high end) to t array
    self.tedges = np.append(self.t, self.thi)
    #print('Trial:', len(self.mu), self.name)
    #exit()
    self.detector = detector


  def alert(self, data):
    sn_distance = data['sn_distance'] if 'sn_distance' in data else self.dist
    new_mu = self.new_mu*(10./sn_distance)**2
    # Define mean (total number of signal events) as the integral of the lightcurve model
    new_mean = sum(new_mu)
    # normalize histogram to unit area
    nmu = new_mu / new_mean
    nmu.flags.writeable = False

    tdelay = data['sig_t_delay'] if 'sig_t_delay' in data else 0
    nev = Node.rng.poisson(new_mean)
    size = len(self.mu)
    j = Node.rng.choice(size, nev, p=nmu, replace=True, shuffle=False)
    t0 = self.tedges[j]
    dt = self.tedges[j+1] - t0
    a = Node.rng.random(nev) * dt + t0 + tdelay
    a.flags.writeable = False

    ngen = { 'times': a, 'gen_t_delay': tdelay }
    if 'gen' in data:
      data['gen'].update(ngen,)
      #rdallava: Combine.py is looking for a tuple. Inserting data['gen'] into a tuple.
      tuple_dict = add_dictionary_to_a_tuple(data['gen'])
      data['gen'] = tuple_dict

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
    data['detector_name'] = self.detector 
    
    return True

