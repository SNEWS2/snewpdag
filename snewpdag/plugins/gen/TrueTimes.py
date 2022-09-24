"""
TrueTimes - generate true arrival times

Arguments:
  detector_location: filename of detector database for DetectorDB
  detectors: list of detectors for which to generate burst times
  ra: right ascension (degrees)
  dec: declination (degrees)
  time: time string, e.g., '2021-11-01 05:22:36.328'
  epoch_base (optional): starting time for epoch, float value or field specifier
    (string or tuple)

Input:
  [epoch_base]: float value of starting time for epoch, in unix epoch

Output:
  truth/true_sn_ra: right ascension (radians)
  truth/true_sn_dec: declination (radians)
  truth/dets/<det_id>/true_t: arrival time, (float) seconds in snewpdag time
"""
import logging
import numbers
import numpy as np
import healpy as hp
from astropy.time import Time
from astropy import constants as const
from astropy import units as u
from astropy.coordinates import GCRS, SkyCoord, CartesianRepresentation

from snewpdag.dag import Node, Detector, DetectorDB
from snewpdag.dag.lib import fetch_field

class TrueTimes(Node):
  def __init__(self, detector_location, detectors, ra, dec, time, **kwargs):
    self.db = DetectorDB(detector_location)
    self.ra = np.radians(ra)
    self.dec = np.radians(dec)
    self.time = Time(time)
    self.time_unix = self.time.to_value('unix', 'long') # float, unix epoch
    self.epoch_base = kwargs.pop('epoch_base', 0.0)

    if not isinstance(epoch_base, [numbers.Number, str, list, tuple]):
      logging.error('TrueTimes.__init__: unrecognized epoch_base {}. Set to 0.'.format(epoch_base))
      self.epoch_base = 0.0

    sc = SkyCoord(ra=ra, dec=dec, unit=u.deg, frame='icrs', \
                  representation_type='unitspherical', obstime=self.time)
    gc = sc.transform_to(GCRS)
    d = gc.represent_as(CartesianRepresentation)
    self.snr = np.array( [ d.x, d.y, d.z ] ) # should be unit length!
    logging.info('ra(lon) = {}, dec(lat) = {}'.format(self.ra, self.dec))
    logging.info('SN location = {}'.format(self.snr))
    self.dets = set(detectors) # detector names
    super().__init__(**kwargs)

  def alert(self, data):
    # record truth information
    if 'truth' not in data:
      data['truth'] = {}
    data['truth']['true_sn_ra'] = self.ra # radians
    data['truth']['true_sn_dec'] = self.dec # radians

    # epoch base
    if isinstance(self.epoch_base, numbers.Number):
      t0 = self.epoch_base
    elif isinstance(self.epoch_base, [str, list, tuple]):
      t0 = fetch_field(data, self.epoch_base)
    time_base = self.time_unix - t0

    # generate true times for each detector.
    # given time is when wavefront arrives at Earth origin.
    ts = {}
    for dname in self.dets:
      #c = 3.0e8 # m/s
      det = self.db.get(dname)
      pos = det.get_xyz(self.time) # detector in GCRS at given time
      logging.info('pos[{}] = {}'.format(dname, pos))
      logging.info('  sn pos = {}'.format(self.snr))
      dt = - np.dot(det.get_xyz(self.time), self.snr) / const.c # intersect
      t1 = time_base + dt.to(u.s).value
      ts[dname] = {
                    'true_t': t1, # s in snewpdag time
                  }

    data['truth']['dets'] = ts
    return data

