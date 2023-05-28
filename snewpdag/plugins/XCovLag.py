"""
XCovLag - calculate best lag between two time series based on cross covariance

Arguments:
  tnbins:  nbins for timing comparison between detectors
  twidth:  timespan (s) for timing histogram
  in_field:  input field for a new time series
  in_det_field:  field containing detector identifier
  in_det_list_field:  field containing list of detectors to match
  out_lags_field:  output field for { det: lag(s) } dict
  lead_time:  start time relative to first event time of first time series
  fixed_ref:  default None, otherwise calculate all lags relative to
    identified detector

lead_time should be -0.1s for signal-only, to make sure one always includes
all of the signal.  When we can assume first event is background,
lead_time can be +0.1s to make sure both start in background.

Default lead_time = -0.1s, i.e., assumes signal-only.
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.values import Hist1D, TimeSeries

class XCovLag(Node):
  def __init__(self, tnbins, twidth,
               in_field, in_det_field, in_det_list_field,
               out_lags_field,
               **kwargs):
    self.tnbins = tnbins # nbins for time histogram
    self.twidth = twidth # time span (s) for histogram
    self.in_field = in_field
    self.in_det_field = in_det_field
    self.in_det_list_field = in_det_list_field
    self.out_lags_field = out_lags_field
    self.lead_time = kwargs.pop('lead_time', -0.1) # 100ms before
    self.fixed_ref = kwargs.pop('fixed_ref', None)
    self.cache = {} # { <det>: <TimeSeries> }
    self.last_burst_report = -1 # only forward one report per burst id
    super().__init__(**kwargs)

  def xcov(self, k1, kref, dt):
    w1 = self.cache[k1]
    w2 = self.cache[kref]
    #st1 = np.min(w1.times) - dt
    #st2 = np.min(w2.times)
    st1 = np.min(w1.times) + self.lead_time # 100ms lead time
    #st2 = np.min(w2.times)
    #st1 = w1.start - dt
    #st2 = w2.start
    #start = np.min(w2.times)
    ##start = np.min([st1, st2])
    ##h1, edges = w1.histogram(self.tnbins, start + dt, start + dt + self.twidth)
    ##h2, edges = w2.histogram(self.tnbins, start, start + self.twidth)
    h1, edges = w1.histogram(self.tnbins, st1, st1 + self.twidth)
    h2, edges = w2.histogram(self.tnbins, st1 - dt, st1 - dt + self.twidth)
    logging.info('{}: xcov dt = {}'.format(self.name, dt))
    logging.info('{}: xcov h1 = {}'.format(self.name, h1))
    logging.info('{}: xcov h2 = {}'.format(self.name, h2))
    return np.sum(h1 * h2)

  def lag(self, k1, kref):
    if k1 == kref:
      return (0.0, 0.0)
    # find best lag
    hdt = 0.0001
    dt = np.arange(-0.05, 0.05, hdt)
    #x = [ self.xcov(k1, kref, dt[i]) for i in range(len(dt)) ]
    #best = np.argmax(x)
    #logging.info('{}: best = {}, x = {}'.format(self.name, best, x))
    # estimate the error by calculating the second derivative
    y = np.array([ self.xcov(k1, kref, dt[i]) for i in range(len(dt)) ])
    yb = np.argmax(y)
    #logging.info('{}: nlog best = {}, y = {}'.format(self.name, yb, y))
    return (dt[yb], 0.0, dt, y)

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

