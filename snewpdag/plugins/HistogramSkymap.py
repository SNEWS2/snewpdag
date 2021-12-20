"""
HistogramSkymap - keep counts in a skymap

Arguments:
  nside: skymap healpix resolution
  in_field: name of input field containing indices to increment
  out_field: name of map output field
  out_err_field: name of map output field containing stddevs

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
    super().__init__(**kwargs)

  def alert(self, data):
    self.m[data[self.in_field]] += 1
    return False

  def reset(self, data):
    return False

  def revoke(self, data):
    return False

  def report(self, data):
    maxv = np.amax(self.m)
    if maxv > 0:
      mm = self.m / maxv
      me = np.sqrt(self.m) / maxv
    else:
      mm = self.m
      me = mm
    data[self.out_field] = mm
    data[self.out_err_field] = me
    return data

