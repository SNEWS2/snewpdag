"""
GenPointDts - generate time differences for a given SN direction

Arguments:
  detector_locations: filename for DetectorDB
  pairs: filename of detector pairs.
    csv with columns det1,det2,dtsig,dtbias.
    dtsig and dtbias are in seconds.
  ra: right ascension (degrees)
  dec: declination (degrees)
  time: time string, e.g., '2021-11-01 05:22:36.328',
        indicating time neutrino wavefront arrives at center of Earth
  smear: (optional, default True) whether to smear output dts
  epoch_base: starting time for epoch, float value or field specifier
    (string or tuple)

Input:
  [epoch_base]: float value of starting time for epoch, in unix epoch

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
import numbers
import numpy as np
import healpy as hp
import csv
from astropy.time import Time
from astropy import constants as const
from astropy import units as u
from astropy.coordinates import GCRS, SkyCoord, CartesianRepresentation

from snewpdag.dag import Node, Detector, DetectorDB
from snewpdag.dag.lib import fetch_field

class GenPointDts(Node):
  def __init__(self, detector_location, pairs, ra, dec, time, **kwargs):
    self.db = DetectorDB(detector_location)
    self.ra = np.radians(ra)
    self.dec = np.radians(dec)
    self.tc = Time(time)
    self.tc_unix = self.tc.to_value('unix', 'long') # float, unix epoch
    self.epoch_base = kwargs.pop('epoch_base', 0.0)

    if not isinstance(self.epoch_base, (numbers.Number, str, list, tuple)):
      logging.error('GenPointDts.__init__: unrecognized epoch_base {}. Set to 0.'.format(self.epoch_base))
      self.epoch_base = 0.0

    self.smear = kwargs.pop('smear', True)

    sc = SkyCoord(ra=ra, dec=dec, unit=u.deg, frame='icrs', \
                  representation_type='unitspherical', obstime=self.tc)
    gc = sc.transform_to(GCRS)
    d = gc.represent_as(CartesianRepresentation)
    self.snr = np.array( [ d.x, d.y, d.z ] ) # should be unit length!
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
    if 'dets' not in data['truth']:
      data['truth']['dets'] = {}
    data['truth']['sn_ra'] = self.ra # radians
    data['truth']['sn_dec'] = self.dec # radians
    data['truth']['time_center'] = self.tc # astropy.Time object

    # calculate arrival of SN time at Earth center in local epoch
    # i.e. subtracting epoch_base
    if isinstance(self.epoch_base, numbers.Number):
      t_epoch = self.epoch_base
    elif isinstance(self.epoch_base, (str, list, tuple)):
      t_epoch, valid = fetch_field(data, self.epoch_base)
      if not valid:
        logging.error('{}: epoch_base field {} not found in payload'.format(self.name, self.epoch_base))
        return False
    else:
      logging.error('{}: unrecognized epoch_base field {}'.format(self.name, self.epoch_base))
      return False
    tc_local = self.tc_unix - t_epoch

    # generate dt for each detector, including bias
    dts = {}
    for p in self.pairs:
      # detector 1 time
      det1 = self.db.get(p['det1'])
      pos1 = det1.get_xyz(self.tc) # detector in GCRS at given time
      t1 = - np.dot(pos1, self.snr) / const.c # intersect
      tt1 = tc_local + t1.to(u.s).value # s
      data['truth']['dets'][p['det1']] = { 'true_t': tt1 }

      # detector 2 nominal time, with bias
      det2 = self.db.get(p['det2'])
      pos2 = det2.get_xyz(self.tc) # detector in GCRS at given time
      t2 = - np.dot(pos2, self.snr) / const.c # intersect
      # bias is det1-det2, so subtract nominal bias from det2
      t2 -= p['dtbias'] * u.second
      # smear detector 2 if requested
      if self.smear:
        t2 += p['dtsig'] * Node.rng.normal() * u.second
      tt2 = tc_local + t2.to(u.s).value
      data['truth']['dets'][p['det2']] = { 'true_t': tt2 }

      dts[(p['det1'],p['det2'])] = {
                 'dt': tt1 - tt2, # s
                 't1': tt1, # s
                 't2': tt2, # s
                 'bias': p['dtbias'], # sec
                 'var': (p['dtsig'])**2, # sec**2
                 'dsig1': 0.0, # sec
                 'dsig2': 0.0, # sec
               }

    data['dts'] = dts
    return data

