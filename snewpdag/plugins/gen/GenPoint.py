"""
GenPoint - generate time differences for a given SN direction
"""
import logging
import numpy as np
import healpy as hp
from astropy.time import Time
from astropy import constants as const
from astropy import units as u

from snewpdag.dag import Node, Detector, DetectorDB
from snewpdag.dag.lib import normalize_time, subtract_time

class GenPoint(Node):
  def __init__(self, detector_location, pair_list, ra, dec, time, **kwargs):
    self.db = DetectorDB(detector_location)
    self.pairs = pair_list
    self.ra = np.radians(ra)
    self.dec = np.radians(dec)
    self.time = Time(time)
    self.smear = kwargs.pop('smear', True)
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
    self.dets = set()
    for p in self.pairs:
      self.dets.add(p[0])
      self.dets.add(p[1])
    super().__init__(**kwargs)

  def alert(self, data):
    # record truth information
    if 'truth' not in data:
      data['truth'] = {}
    data['truth']['sn_ra'] = self.ra # radians
    data['truth']['sn_dec'] = self.dec # radians

    # generate times for each detector, including bias.
    # given time is when wavefront arrives at Earth origin.
    g = 1000000000 / u.second
    ts = {}
    bias = {}
    sigma = {}
    for dname in self.dets:
      #c = 3.0e8 # m/s
      det = self.db.get(dname)
      pos = det.get_xyz(self.time)
      logging.info('pos[{}] = {}'.format(dname, pos))
      logging.info('  sn pos = {}'.format(self.snr))
      dt = - np.dot(det.get_xyz(self.time), self.snr) / const.c # intersect
      logging.info('  dt before bias = {}'.format(dt))
      dt += det.bias * u.second
      if self.smear:
        dt += det.sigma * Node.rng.normal() * u.second # smear (s)
      logging.info('  dt = {}'.format(dt))
      dtt = (self.ttuple[0], self.ttuple[1] + dt * g)
      ts[dname] = normalize_time(dtt)
      bias[dname] = det.bias
      sigma[dname] = det.sigma
      logging.info('  time[{}] = {}'.format(dname, ts[dname]))

    # generate pair times
    dts = {}
    g = 1000000000
    for p in self.pairs:
      dt = subtract_time(ts[p[0]], ts[p[1]])
      logging.info('dt[{}] = {}'.format(p, dt))
      dts[p] = {
                 'dt': dt, # (s, ns)
                 't1': ts[p[0]], # (s, ns)
                 't2': ts[p[1]], # (s, ns)
                 'bias': bias[p[0]] - bias[p[1]], # sec
                 'var': sigma[p[0]]**2 + sigma[p[1]]**2, # sec**2
                 'dsig1': sigma[p[0]], # sec
                 'dsig2': - sigma[p[1]], # sec
               }
    data['dts'] = dts
    return data

