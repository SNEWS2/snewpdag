"""
GenTimeDist:  generates a time distribution on each alert, based on a histogram

configuration:
  field:     field name. Must be TimeSeries or TimeHist. Modified in place.
  sig_mean:  mean number of events to generate.
             If it's a number, use the number itself.  Default is the
               area of the histogram read from the input spectrum.
             If it's a field designator, read from the payload.
  sig_smear: True if apply Poisson fluctuation to mean (optional, def True)
  sig_t0:    observed core bounce time. This will correspond to the t=0
             of the input distribution.  Optional, default 1658580450.0,
               which happens to be sometime on 23 July 2022 in the UK.
             If it's a float, use the number as a timestamp.
             If it's a tuple, interpret as (s,ns) timestamp.
             If it's a field, read the time stamp or (s,ns) from the payload.

  A "field designator" is either a string or tuple of strings
  which navigate into the payload.

Originally based on Vladimir's TimeDistFileInput, via TimeDist

Need a generator for SN direction and core bounce times for each detector.
"""
import logging
import numpy as np
import numbers

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field, ns_per_second
from snewpdag.values import TimeHist, TimeSeries
from . import TimeDistSource

class GenTimeDist(TimeDistSource):

  def __init__(self, sig_mean, field, **kwargs):
    self.sig_mean = sig_mean
    self.field = field
    ts = kwargs.pop('sig_t0', 0.0)
    if isinstance(ts, (list, tuple, str)):
      self.sig_t0 = ts
    elif isinstance(ts, numbers.Number):
      self.sig_t0 = time_tuple_from_float(ts)
    self.sig_smear = kwargs.pop('sig_smear', True)
    super().__init__(**kwargs)
    self.area = np.sum(self.mu)
    self.mu_norm = self.mu / self.area
    self.tedges = np.append(self.t, self.thi) # append high end to t array

  def alert(self, data):
    if self.field in data:
      v = data[self.field]

      # adjust offsets for t0 and TimeSeries reference timestamps.
      # For instance, if core bounce is at 100s, but ref time is 90s,
      # then an event at t=0 should have an offset of 10s.
      if isinstance(self.sig_t0, (str, tuple, list)): # interpret as field
        t0, flag = fetch_field(data, self.sig_t0)
        if not flag:
          logging.error('{}: {} not found in payload'.format(self.name, self.sig_t0))
          return False
      else:
        t0 = self.sig_t0
      logging.debug('{}: t0 = {}, ref time {}'.format(self.name, t0, v.start))
      offset = (t0[0] - v.start[0]) + (t0[1] - v.start[1]) / ns_per_second

      # set mean number of events to generate
      if isinstance(self.sig_mean, numbers.Number):
        mean = self.sig_mean
      else:
        mean, flag = fetch_field(data, self.sig_mean)
        if not flag:
          mean = self.area # area of source histogram

      # Poisson fluctuation in mean, if requested
      nev = Node.rng.poisson(mean) if self.sig_smear else mean

      # generate time series of offsets, with t=0 at core bounce
      j = Node.rng.choice(len(self.mu_norm), nev,
                          p=self.mu_norm, replace=True, shuffle=False)
      ta = self.tedges[j]
      dt = self.tedges[j+1] - ta
      a = ta + Node.rng.random(nev) * dt - offset

      # add offsets in seconds - works for TimeHist or TimeSeries
      v.add_offsets_s(a)
      return data
    else:
      return False

