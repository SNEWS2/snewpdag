"""
NBLag - calculate best lag between time series and template
  based on Poisson likelihood, with background

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

from snewpdag.dag import Node, LogTable
from snewpdag.values import Hist1D, TimeSeries

class NBLag(Node):
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
    self.bg = kwargs.pop('bg', {}) # background rate per second
    self.cache = {} # { <det>: <TimeSeries> }
    self.last_burst_report = -1 # only forward one report per burst id
    self.lt = LogTable()
    super().__init__(**kwargs)

  def xlognm(self, k1, k2, dt):
    w1 = self.cache[k1]
    w2 = self.cache[k2]
    if len(w1.times) == 0 or len(w2.times) == 0:
      logging.error('{}: w1 or w2 empty'.format(self.name))
      logging.error('{}: k1 = {}, len(w1) = {}'.format(self.name, k1, len(w1.times)))
      logging.error('{}: k2 = {}, len(w2) = {}'.format(self.name, k2, len(w2.times)))
      return 0.0
    #st1 = np.min(w1.times) - 0.100 # 100ms lead time
    #st1 = np.min(w1.times) - 2.0 # 1100ms lead time (FA)
    # let's expect (for now) that at least 100ms of background
    # are included.  So we'll set the nominal start time 100ms
    # after the first event in w1.  Then when dt varies over its range,
    # both timeseries will start before the signal really turns on.
    st1 = np.min(w1.times)
    st2 = np.min(w2.times)
    st = st1 if st1 > st2 else st2
    st = st + 0.100 # 100ms buffer time
    h1, edges = w1.histogram(self.tnbins, st, st + self.twidth)
    h2, edges = w2.histogram(self.tnbins, st - dt, st - dt + self.twidth)
    #x = np.sum(sc.gammaln(h1 + h2 + 1.0) - sc.gammaln(h2 + 1.0))

    # need to determine a = signal yield ratio for h2/h1,
    # b is background (per bin) for h1, and c is background for h2.

    s1 = np.sum(h1) - self.bg.get(k1, 0.0) * self.twidth
    s2 = np.sum(h2) - self.bg.get(k2, 0.0) * self.twidth
    a = s2 / s1
    b = self.bg.get(k1, 0.0) * self.twidth / self.tnbins
    c = self.bg.get(k2, 0.0) * self.twidth / self.tnbins
    x = 0.0
    g = (1.0 + a) * (c / a - b)
    lg = np.log(np.fabs(g))
    ba = b*(1.0 + a)
    for k in range(self.tnbins):
      #s = 0.0
      #f = 1.0
      #for j in range(h2[k]+1):
      #  nmj = h1[k] + h2[k] - j
      #  if j > 0:
      #    f = f * g / j
      #  s = s + sc.comb(nmj, h1[k]) * f * sc.gammaincc(nmj + 1, b*(1+a))
      #x = x + np.log(s)
      if g == 0.0:
        s = sc.gammaln(h1[k] + h2[k] + 1) - sc.gammaln(h2[k] + 1) - \
            sc.gammaln(h1[k] + 1) - \
            np.log(sc.gammaincc(h1[k] + h2[k] + 1, ba))
      else:
        j = np.arange(h2[k] + 1)
        sgns = np.ones_like(j)
        if g < 0:
          sgns = (- sgns)**j
        r2 = h1[k] + 1 # n + 1
        r4 = j + 1
        r3 = - j + h2[k] + 1 # m - j + 1
        r1 = r3 + h1[k] # n + m - j + 1
        lx = sc.gammaln(r1) - sc.gammaln(r2) - sc.gammaln(r3) \
             - sc.gammaln(r4) + j * lg
        #+ h2[k] * np.log(a) - (h1[k] + h2[k] + 1) * np.log(a + 1.0)
        gx = sc.gammaincc(r1, ba)
        mask = gx > 0.0
        #logging.info('{}: lx={}'.format(self.name, lx))
        #logging.info('{}: gx={}'.format(self.name, gx))
        #logging.info('{}: mask={}'.format(self.name, mask))
        mx = lx[mask] + np.log(gx[mask])
        msgns = sgns[mask]
        #logging.info('{}: mx({})={}'.format(self.name, len(mx), mx))
        #logging.info('{}: msgns({})={}'.format(self.name, len(msgns), msgns))
        s = sc.logsumexp(mx, b=msgns)
        if np.isnan(s):
          logging.error('{}: exception in logsumexp'.format(self.name))
          logging.error('{}: k={}, h1={}, h2={}'.format(self.name, k, h1[k], h2[k]))
          logging.error('{}: h1={}, h2={}, a={}, b={}, c={}, g={}, lg={}, ba = {}'.format(self.name, np.sum(h1), np.sum(h2), a, b, c, g, lg, ba))
          logging.error('{}: s={}'.format(self.name, s))
          logging.error('{}: mx({})={}'.format(self.name, len(mx), mx))
          logging.error('{}: msgns({})={}'.format(self.name, len(msgns), msgns))
      x = x + s
    return x

  def xprod(self, n, m, a, b, c):
    v = np.zeros((n+1, m+1))
    #ab = - np.log((1.0 + a)*b)
    #ac = np.log(a / ((1.0 + a)*c))
    la = np.log(a)
    la1 = np.log(a+1.0)
    for r in range(n+1):
      #logging.info('{}: n={}, m={}, r={}'.format(self.name, n, m, r))
      j = np.arange(m+1)
      #v[r] = j*ac + r*ab + self.lt.logfact(j+r) \
      #       - self.lt.logfact(r) - self.lt.logfact(n-r) \
      #       - self.lt.logfact(j) - self.lt.logfact(m-j)
      v[r] = (j+r)*la1 - j*la - self.lt.logfact(r) - self.lt.logfact(j) \
             + self.lt.logfact(m+n-j-r) - self.lt.logfact(m-j) \
             - self.lt.logfact(n-r)
    x = sc.logsumexp(v) # sums over all elements
    #logging.info('{}: logsumexp = {}'.format(self.name, x))
    return x

  def xprodnm(self, k1, k2, dt):
    w1 = self.cache[k1]
    w2 = self.cache[k2]
    if len(w1.times) == 0 or len(w2.times) == 0:
      logging.error('{}: w1 or w2 empty'.format(self.name))
      logging.error('{}: k1 = {}, len(w1) = {}'.format(self.name, k1, len(w1.times)))
      logging.error('{}: k2 = {}, len(w2) = {}'.format(self.name, k2, len(w2.times)))
      return 0.0
    #st1 = np.min(w1.times) - 0.100 # 100ms lead time
    #st1 = np.min(w1.times) - 2.0 # 1100ms lead time (FA)
    # let's expect (for now) that at least 100ms of background
    # are included.  So we'll set the nominal start time 100ms
    # after the first event in w1.  Then when dt varies over its range,
    # both timeseries will start before the signal really turns on.
    st1 = np.min(w1.times)
    st2 = np.min(w2.times)
    st = st1 if st1 > st2 else st2
    st = st + 0.100 # 100ms buffer time
    h1, edges = w1.histogram(self.tnbins, st, st + self.twidth)
    h2, edges = w2.histogram(self.tnbins, st - dt, st - dt + self.twidth)
    #x = np.sum(sc.gammaln(h1 + h2 + 1.0) - sc.gammaln(h2 + 1.0))

    # need to determine a = signal yield ratio for h2/h1,
    # b is background (per bin) for h1, and c is background for h2.

    s1 = np.sum(h1) - self.bg.get(k1, 0.0) * self.twidth
    s2 = np.sum(h2) - self.bg.get(k2, 0.0) * self.twidth
    a = s2 / s1
    b = self.bg.get(k1, 0.0) * self.twidth / self.tnbins
    c = self.bg.get(k2, 0.0) * self.twidth / self.tnbins

    x = 0.0
    for k in range(self.tnbins):
      s = self.xprod(h1[k], h2[k], a, b, c)
      #logging.info('{}: time bin = {}, s = {}'.format(self.name, k, s))
      x = x + s
    logging.info('{}: dt = {}, x = {}'.format(self.name, dt, x))
    return x

  def lag(self, k1, kref):
    # find best lag
    hdt = 0.001
    t0 = -0.05
    t1 = 0.05
    #hdt = 0.002 # FA values
    #t0 = -1.0
    #t1 = 1.0
    dt = np.arange(t0, t1, hdt)
    if k1 == kref:
      return { 'dt': 0.0,
               't1': np.min(self.cache[k1].times), \
               't2': np.min(self.cache[kref].times), \
               'bias': 0.0, 'var': 0.0, 'dsig1': 0.0, 'dsig2': 0.0, \
               'profile_x': dt, 'profile_y': np.zeros_like(dt) }

    # estimate the error by calculating the second derivative
    #y = np.array([ self.xlognm(k1, kref, dt[i]) for i in range(len(dt)) ])
    # below is the wrong order for subsequent modules,
    # but it puts the larger detector first in tests,
    # which is what we need to avoid having to use the weights in logsumexp
    #y = np.array([ self.xlognm(kref, k1, dt[i]) for i in range(len(dt)) ])
    y = np.array([ self.xprodnm(k1, kref, dt[i]) for i in range(len(dt)) ])
    yb = np.argmax(y)

    return { 'dt': dt[yb],
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

