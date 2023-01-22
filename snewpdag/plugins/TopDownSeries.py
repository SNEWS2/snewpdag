"""
TopDownSeries - top-down time series comparison, no background

Arguments:
  detector_location:  filename of detector database for DetectorDB
  nside:  healpix nside parameter, i.e., skymap resolution
  tnbins:  nbins for timing comparison between detectors
  twidth:  timespan (s) for timing histogram
  in_field:  input field for a new time series
  in_det_field:  field containing detector identifier
  in_det_list_field:  field containing list of detectors to match
  method:  'poisson' (default) or 'gaussian' (optional approximation)
"""
import logging
import numpy as np
import healpy as hp
import scipy.special as sc
from astropy.time import Time
from astropy import units as u
from astropy import constants as const

from snewpdag.dag import Node, CelestialPixels
from snewpdag.dag import DetectorDB
from snewpdag.values import Hist1D, TimeSeries

class TopDownSeries(Node):
  def __init__(self, detector_location, nside, tnbins, twidth,
               in_field, in_det_field, in_det_list_field,
               method='poisson',
               **kwargs):
    self.db = DetectorDB(detector_location)
    self.nside = nside
    self.npix = hp.nside2npix(nside)
    self.tnbins = tnbins # nbins for time histogram
    self.twidth = twidth # time span (s) for histogram
    self.in_field = in_field
    self.in_det_field = in_det_field
    self.in_det_list_field = in_det_list_field
    self.method = method
    self.cache = {} # { <det> : <TimeSeries> }
    super().__init__(**kwargs)

  def reference_time(self):
    tm = [ np.min(self.cache[k].times) for k in self.cache.keys() ]
    return np.min(tm)

  def compare(self, keys, tdelays):
    """
    Compare timing profiles for one sky position (set of time offsets)
    keys = list of detectors
    tdelays = time offsets in s, shape (nkeys,)
    Return chi2-like measure.
    """
    # find earliest time
    tstart = self.reference_time()
    # bin the time series
    hs = []
    areas = []
    for i in range(len(keys)):
      k = keys[i]
      # tdelays should be in s, but may be wrapped in a dimensionless Quantity
      dt = tdelays[i].value if hasattr(tdelays[i], 'unit') else tdelays[i]
      v = self.cache[k]
      #logging.debug('times = {}'.format(v.times))
      #logging.debug('  hasattr unit tnbins = {}, tstart = {}, dt = {}, twidth = {}'.format(hasattr(self.tnbins, 'unit'), hasattr(tstart, 'unit'), hasattr(dt, 'unit'), hasattr(self.twidth, 'unit')))
      h, edges = v.histogram(self.tnbins,
                             start=tstart - dt,
                             stop=tstart + self.twidth - dt)
      #logging.debug(f'h[{i}] = {h}')
      hs.append(h) # total counts, shape (nkeys, nbins)
      a = np.sum(h)
      areas.append(a)
    nn = np.array(hs)
    aa = np.array(areas)
    aa_sum = np.sum(aa)
    f_t = aa / aa_sum # shape (nkeys,)

    # reference profile
    sigsum = np.sum(nn, 0) # sum within each time bin
    ref = sigsum / np.sum(sigsum) # normalized reference profile

    logging.debug('nn = {}'.format(nn))

    # compare
    chi2 = 0.0
    for i in range(len(aa)): # loop over detectors
      for j in range(len(ref)): # loop over time bins
        if aa[i] > 0:
          pp = aa[i]*ref[j] # predicted area
          ppi = np.floor(pp)
          if pp > 0:
            # unnormalized probability
            #x = nn[i,j] * np.log(pp) - pp - sc.gammaln(nn[i,j] + 1)

            # logl1:
            # probability normalized to 1 at maximum
            #x = (nn[i,j] - ppi) * np.log(pp) + \
            #    sc.gammaln(ppi + 1) - sc.gammaln(nn[i,j] + 1)

            # logl2 ("gaussian"):
            # probability with unknown true value, gaussian approx,
            # norm to 1 at max
            if self.method == 'gaussian':
              d = nn[i,j] - pp
              s = nn[i,j] + pp
              x = 0.5 * np.log(2.0 * pp / s)
              x -= 0.5 * d * d / s
              x += np.log(sc.erfc( - np.sqrt(2.0 * nn[i,j] * pp / s) ) /
                          sc.erfc( - np.sqrt(pp) ))

            # logl3:
            # probability with unknown true value, Poisson, norm to 1 at max
            #ppr = (aa_sum - aa[i]) * ref[j]
            #ppri = np.floor(ppr)
            #x = (nn[i,j] - ppi) * np.log(aa[i])
            #x += (sigsum[j] - nn[i,j] - ppri) * np.log(aa_sum - aa[i])
            #x += sc.gammaln(ppi + 1) - sc.gammaln(nn[i,j] + 1)
            #x += sc.gammaln(ppri + 1) - sc.gammaln(sigsum[j] - nn[i,j] + 1)

            # logl4:
            # binomial
            # (actually looks the same as logl1,
            # but why doesn't it give similar results?)
            #pf = f_t[i] * sigsum[j]
            #logging.debug('i = {}, j = {}, pp = {}, pf = {}'.format(i,j,pp,pf))
            #pfi = np.floor(pf)
            #x = (nn[i,j] - pfi) * np.log(f_t[i]) + \
            #    sc.gammaln(pfi + 1) - sc.gammaln(nn[i,j] + 1)

            # logl5:
            # probability with unknown true value, Poisson, norm to 1 at max
            elif self.method == 'poisson':
              x = (pp - nn[i,j]) * np.log(2.0)
              x += sc.gammaln(pp + 1.0) - sc.gammaln(nn[i,j] + 1.0)
              x += sc.gammaln(pp + nn[i,j] + 1.0) - sc.gammaln(2.0 * pp + 1.0)

            elif self.method == 'poisson1a':
              a = areas[i]
              y = aa_sum
              n = nn[i,j]
              m = sigsum[j] - n # sum over the other detectors
              nu = m * a / (y - a) # prediction for n
              x = (nu - n) * np.log(2.0)
              x += sc.gammaln(nu + 1.0) - sc.gammaln(n + 1.0)
              x += sc.gammaln(nu + n + 1.0) - sc.gammaln(2.0 * nu + 1.0)

            elif self.method == 'poisson2':
              a = areas[i]
              y = aa_sum
              n = nn[i,j]
              m = sigsum[j] - n # sum over the other detectors
              #x = (n - np.floor(a * m / (y - a))) * np.log(a)
              #x -= (n + m - np.floor(y * m / (y - a))) * np.log(y)
              #x += sc.gammaln(n + m + 1) - sc.gammaln(n + 1)
              #x += sc.gammaln(np.floor(a * m / (y - a)) + 1)
              #x -= sc.gammaln(np.floor(y * m / (y - a)) + 1)
              #x += np.log(1.0 - sc.gammaincc(n + m + 1, y))
              #x -= np.log(1.0 - sc.gammaincc(np.floor(y * m / (y - a)) + 1, y))
              npred = a * m / (y - a)
              nmpred = y * m / (y - a)
              x = (n - npred) * np.log(a)
              x -= (n + m - nmpred) * np.log(y)
              x += sc.gammaln(n + m + 1.0) - sc.gammaln(nmpred + 1.0)
              x -= sc.gammaln(n + 1.0) - sc.gammaln(npred + 1.0)
              x += np.log(1.0 - sc.gammaincc(n + m + 1.0, y))
              x -= np.log(1.0 - sc.gammaincc(nmpred + 1.0, y))

            else:
              # unrecognized
              logging.debug('{}: unrecognized method {}'.format(self.name, self.method))
              x = 0.0 # unrecognized

            chi2 += x
    chi2 *= -2.0
    return chi2

  def reevaluate(self, data):
    """
    Call compare() for each skymap pixel
    """
    # get directions for each pixel
    t0 = self.reference_time()
    t0a = Time(t0, format='unix')
    cp = CelestialPixels()
    rs = cp.get_map(self.nside, t0) # shape (3,npix)

    # get nominal time shifts for each detector for each pixel
    keys = list(self.cache.keys())
    nkeys = len(keys)
    pd = np.zeros([nkeys, 3])
    i = 0
    for k in keys:
      det = self.db.get(k) # Detector object
      pd[i] = det.get_xyz(t0a) # GCRS coordinates at time [m]
      i += 1
    tdet = pd @ rs / 3.0e8 # time offsets in s, rel to Earth center
    # shape of tdet should be (nkeys,npix)

    # get reference signal profile for each pixel's hypothetical direction
    m = np.zeros(self.npix)
    for i in range(self.npix):
      m[i] = self.compare(keys, tdet[...,i])

    #logging.debug('m = {}'.format(m))
    chi2_min = m.min()
    logging.debug('min = {}, max = {}'.format(chi2_min, m.max()))
    data['chi2'] = m
    mm = m - chi2_min
    data['map'] = mm
    data['ndof'] = 2 # need to confirm this
    data['map_zeroes'] = np.flatnonzero(mm == 0.0)
    return data

  def alert(self, data):
    logging.debug('{}: alert'.format(self.name))
    logging.debug('{}: pre cached {}'.format(self.name, self.cache.keys()))
    if self.in_field in data and self.in_det_field in data:
      self.cache[data[self.in_det_field]] = data[self.in_field]
      logging.debug('{}: post cached {}'.format(self.name, self.cache.keys()))
      if self.in_det_list_field in data:
        logging.debug('{}: in_det_list_field -> {}'.format(self.name, data[self.in_det_list_field]))
        if set(self.cache.keys()) == set(data[self.in_det_list_field]):
          # evaluate skymap if all the detectors in cache
          return self.reevaluate(data)
    return False

  def revoke(self, data):
    logging.debug('{}: revoke'.format(self.name))
    if self.in_det_field in data:
      k = data[self.in_det_field]
      if k in self.cache:
        del self.cache[k]
        return True # force reevaluations downstream since there's a change
    return False

  def reset(self, data):
    logging.debug('{}: reset'.format(self.name))
    if len(self.cache) > 0:
      self.cache = {}
      return True
    else:
      return False

