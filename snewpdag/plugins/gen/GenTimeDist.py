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
             If it's a field, read the time stamp from the payload.
  sig_once:  True if only generate one series of offsets for ll GenTimeDists's,
             as one might do for a perverse test (default False!).
             Note that the offsets will be shifted according to sig_t0,
             and the number of events will match the first module to run.
  epoch_base (optional): starting time for epoch, float value or field specifier
    (string or tuple)

  A "field specifier" is either a string or tuple of strings
  which navigate into the payload.

Originally based on Vladimir's TimeDistFileInput, via TimeDist

Need a generator for SN direction and core bounce times for each detector.
"""
import logging
import numpy as np
import numbers

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field
from snewpdag.values import Hist1D, TimeSeries
from . import TimeDistSource

class GenTimeDist(TimeDistSource):

  one_series = () # shared time series, if self.sig_once is True
  one_mean = 0 # intended mean of shared time series

  def __init__(self, sig_mean, field, **kwargs):
    self.sig_mean = sig_mean
    self.field = field
    ts = kwargs.pop('sig_t0', 0.0)
    if isinstance(ts, (list, tuple, str)): # field specifier
      self.sig_t0 = ts
    elif isinstance(ts, numbers.Number): # literal
      self.sig_t0 = ts
    self.sig_smear = kwargs.pop('sig_smear', True)
    self.sig_once = kwargs.pop('sig_once', False)
    self.epoch_base = kwargs.pop('epoch_base', 0.0)

    if not isinstance(self.epoch_base, (numbers.Number, str, list, tuple)):
      logging.error('GenTimeDist.__init__: unrecognized epoch_base {}. Set to 0.'.format(self.epoch_base))
      self.epoch_base = 0.0

    super().__init__(**kwargs)
    self.area = np.sum(self.mu)
    self.mu_norm = self.mu / self.area
    self.tedges = np.append(self.t, self.thi) # append high end to t array

    # pre-generate single series
    if self.sig_once and np.shape(GenTimeDist.one_series) == (0,):
      j = Node.rng.choice(len(self.mu_norm), self.sig_mean,
                          p=self.mu_norm, replace=True, shuffle=False)
      ta = self.tedges[j]
      dt = self.tedges[j+1] - ta
      GenTimeDist.one_series = ta + Node.rng.random(self.sig_mean) * dt
      GenTimeDist.one_mean = self.sig_mean

  def alert(self, data):
    v, flag = fetch_field(self.field)
    if flag:

      # epoch base
      if isinstance(self.epoch_base, numbers.Number):
        te = self.epoch_base
      elif isinstance(self.epoch_base, (str, list, tuple)):
        te = fetch_field(data, self.epoch_base)

      # adjust offsets for t0 and TimeSeries reference timestamps.
      # For instance, if core bounce is at 100s, but ref time is 90s,
      # then an event at t=0 should have an offset of 10s.
      if isinstance(self.sig_t0, (str, tuple, list)): # interpret as field
        t0, flag = fetch_field(data, self.sig_t0) # s in unix epoch
        if not flag:
          logging.error('{}: {} not found in payload'.format(self.name, self.sig_t0))
          return False
      else:
        t0 = self.sig_t0

      offset = t0 - te
      logging.debug('{}: t0 = {}, ref time {}, offset {}'.format(self.name, t0, te, offset))

      if self.sig_once:
        n = int(self.sig_mean / GenTimeDist.one_mean)
        b = np.empty((n, len(GenTimeDist.one_series)))
        for i in range(n):
          np.copyto(b[i], GenTimeDist.one_series)
        a = np.ravel(b) # flatten to 1D
      else:
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
        a = ta + Node.rng.random(nev) * dt

      # add offsets in seconds - works for Hist1D or TimeSeries
      a += offset
      v.add(a)
      return data
    else:
      return False

