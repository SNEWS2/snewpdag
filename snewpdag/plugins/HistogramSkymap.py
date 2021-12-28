"""
HistogramSkymap - keep counts in a skymap

Arguments:
  nside: skymap healpix resolution
  in_field: name of input field containing indices to increment
  out_field: name of map output field
  out_err_field: name of map output field containing stddevs
  max: (optional, default 0) normalize such that max is this value, 0 if none
  norm: (optional, default 0) normalize to this area, 0 if none
    (norm takes precedence over max)

Input payload:
  in_field: indices to increment within skymap

Output payload (report only):
  out_field: healpix skymap, norm such that max value is 1 (or 0 if all zero)
"""
import logging
import numpy as np
import healpy as hp

from snewpdag.dag import Node

class HistogramSkymap(Node):
  def __init__(self, nside, in_field, out_field, out_err_field, **kwargs):
    self.in_field = in_field
    self.out_field = out_field
    self.out_err_field = out_err_field
    self.m = np.zeros(hp.nside2npix(nside))
    self.max = kwargs.pop('max', 0)
    self.norm = kwargs.pop('norm', 0)
    super().__init__(**kwargs)

  def alert(self, data):
    weight = 1.0 / len(data[self.in_field])
    self.m[data[self.in_field]] += weight
    return False

  def reset(self, data):
    return False

  def revoke(self, data):
    return False

  def report(self, data):
    mm = self.m # default copy of references
    me = mm
    if self.norm > 0.0:
      area = np.sum(self.m)
      if area > 0.0:
        factor = self.norm / area
        mm = self.m * factor
        me = np.sqrt(self.m) * factor
    elif self.max > 0.0:
      maxv = np.amax(self.m)
      if maxv > 0.0:
        factor = 1.0 / maxv
        mm = self.m * factor
        me = np.sqrt(self.m) * factor
    else:
      me = np.sqrt(self.m) # return counts, so stddev is sqrt(n)
    data[self.out_field] = mm
    data[self.out_err_field] = me
    return data

