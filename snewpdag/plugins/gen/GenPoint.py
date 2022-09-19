"""
GenPoint - generate times and time differences for a given SN direction

Arguments:
  detector_location: filename of detector database for DetectorDB
  pair_list: list of detector pairs for which to generate dts
    (optional, default empty, in which case only generate core bounce times)
  ra: right ascension (degrees)
  dec: declination (degrees)
  time: time string, e.g., '2021-11-01 05:22:36.328'
  smear: (optional, default True) whether to smear output times

ra,dec in ICRS coordinate system.

Output:
  truth/sn_ra: right ascension (radians), ICRS
  truth/sn_dec: declination (radians), ICRS
  truth/dets/<det>/true_t: arrival time of core bounce for det (ns), no bias
  dts/(<det1>,<det2>)/dt: time difference between detectors (ns)
  dts/(<det1>,<det2>)/t1: arrival time for det1 (ns)
  dts/(<det1>,<det2>)/t2: arrival time for det2 (ns)
  dts/(<det1>,<det2>)/bias: bias1 - bias2 (sec)
  dts/(<det1>,<det2>)/var: combined variance (sec^2)
  dts/(<det1>,<det2>)/dsig1: sigma1 (sec)
  dts/(<det1>,<det2>)/dsig2: -sigma2 (sec)
"""
import logging
import numpy as np
import healpy as hp
from astropy.time import Time
from astropy import constants as const
from astropy import units as u
from astropy.coordinates import GCRS, SkyCoord, CartesianRepresentation

from snewpdag.dag import Node, Detector, DetectorDB
from snewpdag.dag.lib import t2ns, ns_per_second

class GenPoint(Node):
  def __init__(self, detector_location, ra, dec, time, **kwargs):
    self.db = DetectorDB(detector_location)
    self.pairs = kwargs.pop('pair_list', ())
    self.ra = np.radians(ra)
    self.dec = np.radians(dec)
    self.time = Time(time)
    self.time_ns = t2ns(self.time.to_value('unix', 'long'))
    self.smear = kwargs.pop('smear', True)

    sc = SkyCoord(ra=ra, dec=dec, unit=u.deg, frame='icrs', \
                  representation_type='unitspherical', obstime=self.time)
    gc = sc.transform_to(GCRS)
    d = gc.represent_as(CartesianRepresentation)
    self.snr = np.array( [ d.x, d.y, d.z ] ) # should be unit length!
    logging.info('ra(lon) = {}, dec(lat) = {}'.format(self.ra, self.dec))
    logging.info('SN location = {}'.format(self.snr))
    self.dets = DetectorDB.dets.keys()
    super().__init__(**kwargs)

  def alert(self, data):
    # record truth information
    if 'truth' not in data:
      data['truth'] = {}
    if 'dets' not in data['truth']:
      data['truth']['dets'] = {}
    data['truth']['sn_ra'] = self.ra # radians
    data['truth']['sn_dec'] = self.dec # radians

    # generate times for each detector, including bias.
    # given time is when wavefront arrives at Earth origin.
    g = ns_per_second
    ts = {}
    bias = {}
    sigma = {}
    for dname in self.dets:
      #c = 3.0e8 # m/s
      det = self.db.get(dname)
      pos = det.get_xyz(self.time) # detector in GCRS at given time
      logging.info('pos[{}] = {}'.format(dname, pos))
      logging.info('  sn pos = {}'.format(self.snr))
      dt = - np.dot(det.get_xyz(self.time), self.snr) / const.c # intersect
      logging.info('  dt before bias = {}'.format(dt))
      # store unbiased time in data['truth']
      tcb = self.time_ns + dt.to(u.s).value * g
      data['truth']['dets'][dname] = { 'true_t': tcb }

      # apply bias and smear
      dt += det.bias * u.s
      if self.smear:
        dt += det.sigma * Node.rng.normal() * u.s # smear (s)
      logging.info('  dt = {}'.format(dt))
      dtt = self.time_ns + dt.to(u.s).value * g
      ts[dname] = dtt
      bias[dname] = det.bias
      sigma[dname] = det.sigma
      logging.info('  time[{}] = {}'.format(dname, ts[dname]))

    # generate pair times
    if len(self.pairs) > 0:
      dts = {}
      for p in self.pairs:
        dt = ts[p[0]] - ts[p[1]] # ns
        logging.info('dt[{}] = {}'.format(p, dt))
        dts[p] = {
                   'dt': dt, # ns
                   't1': ts[p[0]], # ns
                   't2': ts[p[1]], # ns
                   'bias': bias[p[0]] - bias[p[1]], # sec
                   'var': sigma[p[0]]**2 + sigma[p[1]]**2, # sec**2
                   'dsig1': sigma[p[0]], # sec
                   'dsig2': - sigma[p[1]], # sec
                 }
      data['dts'] = dts

    return data

