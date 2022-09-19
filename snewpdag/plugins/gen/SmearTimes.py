"""
SmearTimes - smear true times

Arguments:
  detector_location: filename of detector database for DetectorDB

Input:
  truth/dets/<det_id>/true_t: arrival time ns since unix epoch (int64)

Output:
  truth/dets/det_id>/neutrino_time: smeared time (ns)
  truth/dets/bias: bias (s), from db
  truth/dets/sigma: sigma (s), from db
"""
import logging
import numpy as np
import healpy as hp
from astropy.time import Time
from astropy import constants as const
from astropy import units as u

from snewpdag.dag import Node, Detector, DetectorDB
from snewpdag.dag.lib import ns_per_second

class SmearTimes(Node):
  def __init__(self, detector_location, **kwargs):
    self.db = DetectorDB(detector_location)
    super().__init__(**kwargs)

  def alert(self, data):
    logging.info('truth/dets = {}'.format(data['truth']['dets']))
    for k in data['truth']['dets'].keys():
      #c = 3.0e8 # m/s
      det = self.db.get(k)
      v = data['truth']['dets'][k]
      logging.info('k = {}, v = {}'.format(k, v))
      t0 = v['true_t'] # ns (int64)
      dt = det.bias # bias (s)
      dt += det.sigma * Node.rng.normal() # smear (s)
      dtt = t0 + dt * ns_per_second
      v['neutrino_time'] = dtt
      v['bias'] = det.bias
      v['sigma'] = det.sigma
    return data

