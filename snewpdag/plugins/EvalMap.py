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

from snewpdag.dag import Node, CelestialPixels

class EvalMap(Node):
  def __init__(self, detector_location, nside, in_field, in_det_field, in_det_list_field, **kwargs):
    self.db = DetectorDB(detector_location)
    self.nside = nside
    self.npix = hp.nside2npix(nside)
    self.in_field = in_field
    self.in_det_field = in_det_field
    self.in_det_list_field = in_det_list_field
    self.cache = {} # { <det> : <TimeSeries or TimeHist> }
    super().__init__(kwargs)

  def reference_time(self):
    """
    Calculate earliest reference time over the detectors in the cache.
    Assume neutrino burst time for each detector is reflected in
    the TimeHist or TimeSeries reference time.
    Return unix timestamp.
    """
    ts = [ self.cache[k].reference[0] for k in self.cache.keys() ]
    return np.min(ts)

  def compare(self, keys, tdelay):
    """
    tdelay = time offsets in s, shape (nkeys,)
    Return chi2-like measure.
    """
    # Choose TimeHist with coarsest binning to set t=0
    # so we don't have to rebin it.
    # if there were no TimeHists, then we'll just use first (ic=0).
    ic = 0
    max_width = 0.0
    for i in range(nkeys):
      k = keys[i]
      v = self.cache[k]
      if isinstance(v, TimeHist):
        bin_width = v.duration / v.nbins # seconds
        if bin_width > max_width:
          max_width = bin_width
          ic = i

    # choose binning
    v = self.cache[keys[ic]]
    if max_width > 0.0:
      ref_nbins = v.nbins
      ref_duration = v.duration
      ref_start = v.start
      ref_reference = v.reference
    else:
      ref_nbins = 1000
      ref_duration = 10.0 # should really choose shortest duration TimeSeries
      ref_start = v.start
      ref_reference = v.reference

    # rebin all the time profiles, subtracting signals.
    # Estimate signals with 1s data before reference time.
    ns = []
    sigs = []
    bgrs = [] # per bin
    areas = []
    for i in range(nkeys):
      k = keys[i]
      v = self.cache[k]
      t0 = subtract_time(v.reference, (1,0))
      bg = v.integral(t0, v.reference) * ref_duration / ref_nbins
      h, bin_edges = v.histogram(ref_nbins, ref_duration, ref_start)
      sig = h - bg
      a = np.sum(h) # signal area. Could be zero or negative.
      hs.append(h) # total counts, shape (nkeys,nbins)
      sigs.append(sig) # shape (nkeys,nbins)
      bgrs.append(bg)
      areas.append(a)
    nn = np.array(hs)
    ss = np.array(sigs)
    bb = np.array(bgrs)
    aa = np.array(areas)

    # evaluate reference signal profile
    sigsum = np.sum(ss, 0)
    ref = sigsum / np.sum(sigsum)

    # compare 
    chi2 = 0.0
    for i in range(nkeys):
      if areas[i] > 0:
        pp = aa[i]*ss[i] + bb[i]
        chi2 += nn[i] * np.log(pp) - pp - sc.gammaln(nn[i])
    chi2 *= -2.0
    return chi2

  def reevaluate(self, data):
    # get directions to evaluate
    t0 = self.reference_time()
    t0a = Time(t0, format='unix')
    cp = CelestialPixels()
    rs = cp.get_map(self.nside, t0) # shape (3,npix)

    # get nominal time shifts for each detector for each pixel
    keys = self.cache.keys()
    nkeys = len(keys)
    pd = np.zeros([nkeys,3])
    for i in range(nkeys):
      k = keys[i]
      det = self.db.get(k) # Detector object
      pd[i] = det.get_xyz(t0a) # GCRS coordinates at time [m]
    tdet = pd @ rs / 3.0e8 # time offsets in s, rel to Earth center
    # shape of tdet should be (nkeys,npix)

    # get reference signal profile for each pixel's hypothetical direction
    m = np.zeros(self.npix)
    for i in range(self.npix):
      m[i] = self.compare(keys, tdet[i])

    chi2_min = m.min()
    m -= chi2_min
    data['map'] = m
    data['ndof'] = 2 # need to confirm this
    return data

  def alert(self, data):
    if self.in_field in data:
      if self.in_det_field in data:
        self.cache[data[self.in_det_field]] = data[self.in_field]
        if self.in_det_list_field in data:
          if set(self.cache.keys()) == set(data[self.in_det_list_field]):
            # evaluate skymap
            return self.reevaluate(self, data)
    return False

  def revoke(self, data):
    if self.in_det_field in data:
      k = data[self.in_det_field]
      if k in self.cache:
        del self.cache[k]
        return True # force reevaluations downstream since there's a change
    return False

