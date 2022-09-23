"""
SmearTimes - smear true times

Arguments:
  detector_location: filename of detector database for DetectorDB

Input:
  truth/dets/<det_id>/true_t: arrival time, s in unix time

Output:
  observed/dets/<det_id>/neutrino_time: smeared time (s)
  observed/dets/<det_id>/bias: bias (s), from db
  observed/dets/<det_id>/sigma: sigma (s), from db
"""
import logging
import numpy as np
import healpy as hp

from snewpdag.dag import Node, Detector, DetectorDB

class SmearTimes(Node):
  def __init__(self, detector_location, **kwargs):
    self.db = DetectorDB(detector_location)
    super().__init__(**kwargs)

  def alert(self, data):
    logging.info('truth/dets = {}'.format(data['truth']['dets']))
    if 'observed' not in data:
      data['observed'] = { 'dets': {} }
    elif 'dets' not in data['observed']:
      data['observed']['dets'] = {}
    d = data['observed']['dets']
    for k in data['truth']['dets'].keys():
      det = self.db.get(k)
      v = data['truth']['dets'][k]
      logging.info('k = {}, v = {}'.format(k, v))
      t0 = v['true_t'] # (s)
      dt = det.bias # bias (s)
      dt += det.sigma * Node.rng.normal() # smear (s)
      d[k] = {
               'neutrino_time': t0 + dt,
               'bias': det.bias,
               'sigma': det.sigma,
             }
    return data

