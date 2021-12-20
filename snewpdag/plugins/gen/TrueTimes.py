"""
TrueTimes - generate true times
"""
import logging
import numpy as np
import healpy as hp
from astropy.time import Time
from astropy import constants as const
from astropy import units as u

from snewpdag.dag import Node, Detector, DetectorDB
from snewpdag.dag.lib import normalize_time

class TrueTimes(Node):
  def __init__(self, detector_location, detectors, ra, dec, time, **kwargs):
    self.db = DetectorDB(detector_location)
    self.ra = np.radians(ra)
    self.dec = np.radians(dec)
    self.time = Time(time)
    t = self.time.to_value('unix', 'long')
    ti = int(t)
    tf = t - ti
    g = 1000000000
    self.ttuple = (ti, int(tf * g))
    self.snr = np.array([ np.cos(self.dec)*np.cos(self.ra),
                          np.cos(self.dec)*np.sin(self.ra),
                          np.sin(self.dec) ])
    logging.info('ra(lon) = {}, dec(lat) = {}'.format(self.ra, self.dec))
    logging.info('SN location = {}'.format(self.snr))
    self.dets = set(detectors)
    super().__init__(**kwargs)

  def alert(self, data):
    # record truth information
    if 'truth' not in data:
      data['truth'] = {}
    data['truth']['true_sn_ra'] = self.ra # radians
    data['truth']['true_sn_dec'] = self.dec # radians

    # generate true times for each detector.
    # given time is when wavefront arrives at Earth origin.
    g = 1000000000 / u.second
    ts = {}
    for dname in self.dets:
      #c = 3.0e8 # m/s
      det = self.db.get(dname)
      pos = det.get_xyz(self.time)
      logging.info('pos[{}] = {}'.format(dname, pos))
      logging.info('  sn pos = {}'.format(self.snr))
      dt = - np.dot(det.get_xyz(self.time), self.snr) / const.c # intersect
      dtt = (self.ttuple[0], self.ttuple[1] + dt * g)
      ts[dname] = {
                    'true_t': normalize_time(dtt), # (s, ns)
                  }

    data['truth']['dets'] = ts
    return data

