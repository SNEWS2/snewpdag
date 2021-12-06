"""
DiffPointing: generate a skymap of SN direction chi2's
  based on Wiktor Jasniak's Chi2Calculation

Arguments:
  detector_location: filename of detector database for DetectorDB
  nside: healpix nside parameter, i.e., skymap resolution
  min_dts: minimum number of time differences in order to do calculation

Input payload:
  dts: a dictionary of time differences. Keys are of form (det1,det2),
    a list or tuple of detector names (as given in DetectorDB).  The values
    are themselves dictionaries with the following keys:
    required:
      dt: time tuple (s,ns) of t1-t2.
      t1: burst time tuple (s,ns) of det1.
      t2: burst time tuple (s,ns) of det2.
    optional (values derived from DetectorDB if not present):
      bias: bias in dt in seconds, given as bias1-bias2.
      var: variance (stddev**2) of dt in seconds.
      dsig1: (d(dt)/dt1) * sigma1, in seconds, for covariance calculation.
      dsig2: (d(dt)/dt2) * sigma2, in seconds, for covariance calculation.

Output payload:
  map: healpix map with specified nside, nested ordering.
  ndof: 2
"""
import logging
import numpy as np
import healpy as hp

from snewpdag.dag import Node, Detector, DetectorDB
from snewpdag.dag.lib import normalize_time
from astropy.time import Time

class DiffPointing(Node):
  def __init__(self, detector_location, nside, min_dts, **kwargs):
    self.db = DetectorDB(detector_location)
    self.nside = nside
    self.npix = hp.nside2npix(nside)
    self.min_dts = min_dts
    self.cache = {} # (det1, det2): dt, t1, t2, bias, var, dsig1, dsig2
    super().__init__(**kwargs)

  def cache_values(self, k1, k2, dts):
    d1 = self.db.get(k1)
    d2 = self.db.get(k2)
    if 'dt' in dts and 't1' in dts and 't2' in dts:
      dt = dts['dt'] # (s, ns)
      t1 = dts['t1'] # (s, ns)
      t2 = dts['t2'] # (s, ns)
    else:
      return None
    bias = dts['bias'] if 'bias' in dts else d1.bias - d2.bias # sec
    var = dts['var'] if 'var' in dts else d1.sigma**2 + d2.sigma**2 # sec**2
    dsig1 = dts['dsig1'] if 'dsig1' in dts else d1.sigma # sec
    dsig2 = dts['dsig2'] if 'dsig2' in dts else - d2.sigma # sec
    # we actually want a time basis in ms for all times
    g = 1.0e-6
    nrow = {
             'dt': dt[0]*1000 + dt[1]*g,
             't1': t1[0]*1000 + t1[1]*g,
             't2': t2[0]*1000 + t2[1]*g,
             'bias': bias * 1000,
             'var': var * 1000 * 1000,
             'dsig1': dsig1 * 1000,
             'dsig2': dsig2 * 1000,
           }
    logging.info('cache ({}, {}): {}'.format(k1, k2, nrow))
    return nrow

  def d_vectors(self, keys, directions):
    """
    Calculate difference vectors (nv = number of vectors)
    Arguments:
      keys = ordered list of keys of (det1, det2).
      directions = direction hypotheses, Cartesian unit vector, shape [3,nv]
    Returns vector as np.array with shape [nv,nkeys]
    """
    rc = 1.0 / 3.0e5 # 1/(m/ms)
    nkeys = len(keys) # number of detector pairs
    ddt = np.zeros(nkeys)
    p1 = np.zeros([nkeys,3])
    p2 = np.zeros([nkeys,3])
    i = 0
    for k in keys:
      det1 = self.db.get(k[0])
      det2 = self.db.get(k[1])
      dts = self.cache[k]
      ddt[i] = dts['dt'] - dts['bias']
      # remember that t1 and t2 are in ms, not s!
      p1[i] = det1.get_xyz(Time(dts['t1']*0.001, format='unix')) # m
      p2[i] = det2.get_xyz(Time(dts['t2']*0.001, format='unix'))
      i += 1
    dp = (p1 - p2) * rc # ms, shape [nkeys,3]
    d = np.transpose(dp @ directions) # [nv,nkeys]
    d = d + ddt # broadcast adding ddt to each column
    logging.info('ddt = {}'.format(ddt))
    logging.info('dp = {}'.format(dp))
    return d

  def weight_matrix(self, keys):
    """
    Calculate weight matrix.
    Arguments:
      keys = ordered list of keys of (det1, det2).
    Returns matrix as np.array, columns/rows ordered as in keys.
    """
    dim = len(self.cache)
    v = np.zeros([dim, dim])
    i = 0
    for k1 in keys:
      d1 = self.cache[k1]
      j = 0
      for k2 in keys:
        d2 = self.cache[k2]
        if i == j:
          v[i,j] = d2['var']
        else:
          if k1[0] == k2[0]:
            v[i,j] = d1['dsig1'] * d2['dsig1']
          elif k1[1] == k2[1]:
            v[i,j] = d1['dsig2'] * d2['dsig2']
          elif k1[0] == k2[1]:
            v[i,j] = d1['dsig1'] * d2['dsig2']
          elif k1[1] == k2[0]:
            v[i,j] = d1['dsig2'] * d2['dsig1']
        j += 1
      i += 1
    # then invert the matrix
    logging.info('covariance matrix = {}'.format(v))
    return np.linalg.inv(v)

  def reevaluate(self, data):
    """
    Reevaluate direction based on available time differences
    """
    keys = self.cache.keys() # keep list to preserve order
    w = self.weight_matrix(keys) # shape [nkeys,nkeys]

    m = np.zeros(self.npix)
    rs = hp.pixelfunc.pix2vec(self.nside, range(self.npix), nest=True)
    # rs will be an np.array of x,y,z values, each triple a unit vector.
    # however, it'll be returned in shape [3,npix]
    d = self.d_vectors(keys, rs) # returns shape [npix,nkeys]
    dw = d @ w # returns shape [npix,nkeys]
    for i in range(self.npix):
      m[i] = np.dot(dw[i], d[i])

    chi2_min = m.min()
    m -= chi2_min
    data['map'] = m
    data['ndof'] = 2
    return data

  def alert(self, data):
    if 'dts' in data: # dictionary of time differences
      for k in data['dts']:
        # verify that the detector is in the database
        if self.db.has(k[0]) and self.db.has(k[1]):
          # check if it's already in the cache. If so, delete it.
          if k in self.cache:
            self.cache.pop(k)
          else:
            krev = (k[1], k[0]) # reverse order
            if krev in self.cache:
              self.cache.pop(krev)

          nrow = self.cache_values(k[0], k[1], data['dts'][k])
          if nrow != None:
            self.cache[k] = nrow

    if len(self.cache) >= self.min_dts:
      return self.reevaluate(data)
    else:
      return False

  def revoke(self, data):
    if 'dts' in data:
      for k in data['dts']:
        # verify that the detector is in the database
        if self.db.has(k[0]) and self.db.has(k[1]):
          # check if it's already in the cache. If so, delete it.
          if k in self.cache:
            self.cache.pop(k)
          else:
            krev = (k[1], k[0]) # reverse order
            if krev in self.cache:
              self.cache.pop(krev)

    if len(self.cache) >= self.min_dts:
      return self.reevaluate(data)
    else:
      return True

