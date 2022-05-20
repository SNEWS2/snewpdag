"""
GenPointDts - generate time differences for a given SN direction

Arguments:
  detector_locations: filename for DetectorDB
  pairs: filename of detector pairs.
    csv with columns det1,det2,dtsig,dtbias.
    dtsig and dtbias are in seconds.
  ra: right ascension (degrees)
  dec: declination (degrees)
  time: time string, e.g., '2021-11-01 05:22:36.328'
  smear: (optional, default True) whether to smear output dts

Output:
  truth/sn_ra: right ascension (radians)
  truth/sn_dec: declination (radians)
  dts/(<det1>,<det2>)/dt: time difference between detectors (s, ns)
  dts/(<det1>,<det2>)/t1: arrival time for det1 (s, ns)
  dts/(<det1>,<det2>)/t2: arrival time for det2 (s, ns)
  dts/(<det1>,<det2>)/bias: bias1 - bias2 (sec)
  dts/(<det1>,<det2>)/var: combined variance (sec^2)
  dts/(<det1>,<det2>)/dsig1: sigma1 (sec)
  dts/(<det1>,<det2>)/dsig2: -sigma2 (sec)

Note that we leave t1 the same as nominal, and add dt to t2.
This means a single detector may appear to have different event times,
but we'll neglect this for now because DiffPointing only uses the
individual event times to get the detector locations, and those
won't change much.
"""
import logging
import numpy as np
import healpy as hp
import csv
from astropy.time import Time
from astropy import constants as const
from astropy import units as u

from snewpdag.dag import Node, Detector, DetectorDB
from snewpdag.dag.lib import normalize_time, subtract_time

class GenPointDts(Node):
  def __init__(self, detector_location, pairs, ra, dec, time, **kwargs):
    self.db = DetectorDB(detector_location)
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
    # read pair database
    self.pairs = []
    with open(pairs, 'r') as f:
      cr = csv.reader(f)
      for pair in cr:
        p = {
              'det1': pair[0],
              'det2': pair[1],
              'dtsig': float(pair[2]),
              'dtbias': float(pair[3]),
            }
        self.pairs.append(p)
    super().__init__(**kwargs)

  def alert(self, data):
    # record truth information
    if 'truth' not in data:
      data['truth'] = {}
    data['truth']['sn_ra'] = self.ra # radians
    data['truth']['sn_dec'] = self.dec # radians

    # generate dt for each detector, including bias
    dts = {}
    g = 1000000000 / u.second
    for p in self.pairs:
      # detector 1 time
      det1 = self.db.get(p['det1'])
      pos1 = det1.get_xyz(self.time)
      t1 = - np.dot(pos1, self.snr) / const.c # intersect
      tt1 = (self.ttuple[0], int(self.ttuple[1] + t1 * g))

      # detector 2 nominal time, with bias
      det2 = self.db.get(p['det2'])
      pos2 = det2.get_xyz(self.time)
      t2 = - np.dot(pos2, self.snr) / const.c # intersect
      # bias is det1-det2, so subtract nominal bias from det2
      t2 -= p['dtbias'] * u.second
      # smear detector 2 if requested
      if self.smear:
        t2 += p['dtsig'] * Node.rng.normal() * u.second
      tt2 = (self.ttuple[0], int(self.ttuple[1] + t2 * g))

      dts[(p['det1'],p['det2'])] = {
                 'dt': subtract_time(tt1, tt2), # (s, ns)
                 't1': tt1, # (s, ns)
                 't2': tt2, # (s, ns)
                 'bias': p['dtbias'], # sec
                 'var': (p['dtsig'])**2, # sec**2
                 'dsig1': 0.0, # sec
                 'dsig2': 0.0, # sec
               }

    data['dts'] = dts
    return data

