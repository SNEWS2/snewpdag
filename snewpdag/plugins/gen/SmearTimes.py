"""
SmearTimes - smear true times
"""
import logging
import numpy as np
import healpy as hp
from astropy.time import Time
from astropy import constants as const
from astropy import units as u

from snewpdag.dag import Node, Detector, DetectorDB
from snewpdag.dag.lib import normalize_time, subtract_time

class SmearTimes(Node):
  def __init__(self, detector_location, **kwargs):
    self.db = DetectorDB(detector_location)
    super().__init__(**kwargs)

  def alert(self, data):
    g = 1000000000 / u.second
    logging.info('truth/dets = {}'.format(data['truth']['dets']))
    for k in data['truth']['dets'].keys():
      #c = 3.0e8 # m/s
      det = self.db.get(k)
      v = data['truth']['dets'][k]
      logging.info('k = {}, v = {}'.format(k, v))
      t0 = v['true_t'] # (s, ns)
      dt = det.bias * u.second # bias (s)
      dt += det.sigma * Node.rng.normal() * u.second # smear (s)
      dtt = (t0[0], t0[1] + dt * g)
      v['neutrino_time'] = normalize_time(dtt)
      v['bias'] = det.bias
      v['sigma'] = det.sigma
    return data

