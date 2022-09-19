"""
EvalMap - skymap evaluation of some function of input data and
  nominal detector times.

Arguments:
  in_field:  input field for a new time series
  in_det_field:  field containing detector identifier
  in_det_list_field:  field containing list of detectors to match
"""
import logging
import numpy as np
import healpy as hp
import scipy.special as sc
from astropy.time import Time

from snewpdag.dag import Node, CelestialPixels
from snewpdag.dag import DetectorDB
from snewpdag.values import THist, TSeries
from snewpdag.dag.lib import subtract_time, ns_per_second

class EvalMap(Node):
  def __init__(self, detector_location, nside, in_field, in_det_field, in_det_list_field, **kwargs):
    self.db = DetectorDB(detector_location)
    self.nside = nside
    self.npix = hp.nside2npix(nside)
    self.in_field = in_field
    self.in_det_field = in_det_field
    self.in_det_list_field = in_det_list_field
    self.cache = {} # { <det> : <TSeries or THist> }
    super().__init__(**kwargs)

  def reference_time(self):
    """
    Calculate earliest reference time over the detectors in the cache.
    Assume neutrino burst time for each detector is reflected in
    the THist or TSeries reference time.
    Return unix timestamp.
    """
    ts = [ self.cache[k].reference for k in self.cache.keys() ]
    return np.min(ts) / ns_per_second

  def compare(self, keys, tdelay):
    """
    Compare timing profiles for one sky position (set of time offsets)
    keys = list of detectors
    tdelay = time offsets in s, shape (nkeys,)
    Return chi2-like measure.
    """
    # Choose THist with coarsest binning to set t=0
    # so we don't have to rebin it.
    # if there were no THists, then we'll just use first.
    kc = None
    max_width = 0.0
    for k in keys:
      if kc == None:
        kc = k
      v = self.cache[k]
      if isinstance(v, THist):
        bin_width = v.xwidth / v.nbins # seconds
        if bin_width > max_width:
          max_width = bin_width
          kc = k

    # choose binning
    v = self.cache[kc]
    if max_width > 0.0:
      ref_nbins = v.nbins
      ref_duration = v.xwidth # s
      ref_start = v.start # ns relative to ref_reference
      # PROBLEM: not all TSeries has a start field anymore;
      # this reflects prior confusion between start and ref time.
      ref_reference = v.reference # ns
    else:
      ref_nbins = 100
      ref_duration = 10.0 # should really choose shortest duration TSeries
      ref_start = v.start # ns relative to ref_reference
      ref_reference = v.reference # ns

    # rebin all the time profiles, subtracting signals.
    # Estimate signals with 1s data before reference time.
    i = 0
    hs = []
    sigs = []
    bgrs = [] # per bin
    areas = []
    for k in keys:
      v = self.cache[k]
      t0 = v.reference - ns_per_second # precede by 1s
      bg = v.integral(start=t0, stop=v.reference) * ref_duration / ref_nbins
      dt = np.int64(tdelay[i] * ns_per_second)
      tstart = ref_start - dt # ns
      logging.debug('{}: tstart={}, dur={}'.format(self.name, tstart, ref_duration))
      h = v.histogram(ref_nbins, tstart, tstart + ref_duration*ns_per_second)
      sig = h - bg
      hs.append(h) # total counts, shape (nkeys,nbins)
      sigs.append(sig) # shape (nkeys,nbins)
      bgrs.append(bg)
      a = np.sum(sig) # signal area. Could be zero or negative.
      areas.append(a)
      i += 1
    nn = np.array(hs)
    ss = np.array(sigs)
    bb = np.array(bgrs)
    aa = np.array(areas)

    # evaluate reference signal profile
    sigsum = np.sum(ss, 0)
    ref = sigsum / np.sum(sigsum)
    logging.debug('observed  = {}'.format(nn))
    logging.debug('signal    = {}'.format(ss))
    logging.debug('reference = {}'.format(sigsum))

    # compare 
    chi2 = 0.0
    for i in range(len(bb)): # loop over detectors
      for j in range(len(ref)): # loop over time bins
        if aa[i] > 0:
          pp = aa[i]*ref[j] + bb[i]
          if pp > 0:
            x = nn[i,j] * np.log(pp) - pp - sc.gammaln(nn[i,j] + 1)
            chi2 += x
            #logging.debug('  {},{}:  a={}, ref={}, b={}, n={} -> pp={} x={} chi2={}'.format(j,i,aa[i],ref[j],bb[i],nn[i,j],pp,x,chi2))
    chi2 *= -2.0
    return chi2

  def reevaluate(self, data):
    # get directions to evaluate
    t0 = self.reference_time()
    t0a = Time(t0, format='unix')
    cp = CelestialPixels()
    rs = cp.get_map(self.nside, t0) # shape (3,npix)

    # get nominal time shifts for each detector for each pixel
    keys = list(self.cache.keys()) # make a list to preserve order
    nkeys = len(keys)
    pd = np.zeros([nkeys,3])
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
      logging.debug('i={} tdelays = {}'.format(i, tdet[...,i]))
      m[i] = self.compare(keys, tdet[...,i])

    #logging.debug('{}: map {}'.format(self.name, m))
    chi2_min = m.min()
    m -= chi2_min
    data['map'] = m
    data['ndof'] = 2 # need to confirm this
    return data

  def alert(self, data):
    logging.debug('{}: alert'.format(self.name))
    if self.in_field in data:
      if self.in_det_field in data:
        self.cache[data[self.in_det_field]] = data[self.in_field]
        if self.in_det_list_field in data:
          if set(self.cache.keys()) == set(data[self.in_det_list_field]):
            # evaluate skymap
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

