"""
NLogLag - calculate best lag between time series and template
  based on Poisson likelihood

Arguments:
  tnbins:  nbins for timing comparison between detectors
  twidth:  timespan (s) for timing histogram
  in_field:  input field for a new time series
  in_det_field:  field containing detector identifier
  in_det_list_field:  field containing list of detectors to match
  out_lags_field:  output field for { det: lag(s) } dict
    (one half of the interval which contains all points within logL interval)
  fixed_ref:  default None, otherwise calculate all lags relative to
    identified detector
"""
import logging
import numpy as np
import scipy.special as sc

from snewpdag.dag import Node
from snewpdag.values import Hist1D, TimeSeries

class NLogLag(Node):
  def __init__(self, tnbins, twidth,
               in_field, in_det_field, in_det_list_field,
               out_lags_field,
               fixed_ref = None,
               **kwargs):
    self.tnbins = tnbins # nbins for time histogram
    self.twidth = twidth # time span (s) for histogram
    self.in_field = in_field
    self.in_det_field = in_det_field
    self.in_det_list_field = in_det_list_field
    self.out_lags_field = out_lags_field
    self.fixed_ref = fixed_ref
    self.cache = {} # { <det>: <TimeSeries> }
    self.last_burst_report = -1 # only forward one report per burst id
    super().__init__(**kwargs)

  def xlognm(self, k1, k2, dt):
    w1 = self.cache[k1]
    w2 = self.cache[k2]
    if len(w1.times) == 0 or len(w2.times) == 0:
      logging.error('{}: w1 or w2 empty'.format(self.name))
      logging.error('{}: k1 = {}, len(w1) = {}'.format(self.name, k1, len(w1.times)))
      logging.error('{}: k2 = {}, len(w2) = {}'.format(self.name, k2, len(w2.times)))
      return 0.0
    st1 = np.min(w1.times) - 0.100 # 100ms lead time
    #st1 = np.min(w1.times) - 2.0 # 1100ms lead time (FA)
    h1, edges = w1.histogram(self.tnbins, st1, st1 + self.twidth)
    h2, edges = w2.histogram(self.tnbins, st1 - dt, st1 - dt + self.twidth)
    x = np.sum(sc.gammaln(h1 + h2 + 1.0) - sc.gammaln(h2 + 1.0))
    return x

  def lag(self, k1, kref):
    if k1 == kref:
      return (0.0, 0.0)
    # find best lag
    hdt = 0.0001
    t0 = -0.05
    t1 = 0.05
    #hdt = 0.002 # FA values
    #t0 = -1.0
    #t1 = 1.0
    dt = np.arange(t0, t1, hdt)
    # estimate the error by calculating the second derivative
    y = np.array([ self.xlognm(k1, kref, dt[i]) for i in range(len(dt)) ])
    yb = np.argmax(y)

    return { 'dt': dt[yb], \
             't1': np.min(self.cache[k1].times), \
             't2': np.min(self.cache[kref].times), \
             'bias': 0.0, 'var': 0.0, 'dsig1': 0.0, 'dsig2': 0.0, \
             'profile_x': dt, 'profile_y': y }

  def reevaluate(self, data):
    iref = -1
    ks = [ k for k in self.cache.keys() ]
    if self.fixed_ref != None:
      if self.fixed_ref in ks:
        iref = ks.index(self.fixed_ref)
    if iref < 0:
      # choose the detector with the most events as the reference
      ys = [ self.cache[ks[i]].integral() for i in range(len(ks)) ]
      iref = np.argmax(ys) # index of reference detector
    lags = { (ks[j],ks[iref]):self.lag(ks[j], ks[iref]) for j in range(len(ks)) }
    data[self.out_lags_field] = lags
    return data

  def alert(self, data):
    if self.in_field in data and self.in_det_field in data:
      self.cache[data[self.in_det_field]] = data[self.in_field]
      if self.in_det_list_field in data:
        if set(self.cache.keys()) == set(data[self.in_det_list_field]):
          return self.reevaluate(data)
    return False

  def revoke(self, data):
    if self.in_det_field in data:
      k = data[self.in_det_field]
      if k in self.cache:
        del self.cache[k]
        return True
    return False

  def reset(self, data):
    if len(self.cache) > 0:
      self.cache = {}
      return True
    else:
      return False

  def report(self, data):
    if 'burst_id' in data:
      if data['burst_id'] == self.last_burst_report:
        return False
      else:
        self.last_burst_report = data['burst_id']
        return True
    else:
      return True

