"""
LMap - a skymap of likelihoods.

The map will stored in self.map, and is in nested order.
"""
import logging
import numbers
import collections
import numpy as np
import healpy as hp

class LMap:
  def __init__(self, a=0):
    if isinstance(a, numbers.Number):
      if a == 0:
        self.map = np.ones(hp.nside2npix(2)) # placeholder
      else:
        # interpret as nside
        self.map = np.ones(hp.nside2npix(a))
    elif isinstance(a, (collections.Sequence, np.ndarray)):
      self.map = np.array(a)
    else:
      logging.error('LMap.__init__: unrecognized type')
      self.map = np.ones(hp.nside2npix(2)) # placeholder

  def clear(self):
    self.map = np.ones(len(self.map))

  def copy(self):
    return LMap(self.map.copy())

  def combine(self, other):
    if len(self.map) > len(other):
      nside = hp.npix2nside(len(self.map))
      ma = hp.ud_grade(np.array(other), nside,
                       order_in='NESTED', outer_out='NESTED')
    elif len(self.map) < len(other):
      nside = hp.npix2nside(len(other))
      self.map = hp.ud_grade(np.array(self.map), nside,
                             order_in='NESTED', outer_out='NESTED')
      ma = other
    else:
      ma = np.array(other)
    self.map *= ma

