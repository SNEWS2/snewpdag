"""
TrueTimes - generate true arrival times

Arguments:
  detector_location: filename of detector database for DetectorDB
  detectors: list of detectors for which to generate burst times
  ra: right ascension (degrees)
  dec: declination (degrees)
  time: time string, e.g., '2021-11-01 05:22:36.328'

Output:
  truth/true_sn_ra: right ascension (radians)
  truth/true_sn_dec: declination (radians)
  truth/dets/<det_id>/true_t: arrival time (s, ns), s in unix time
"""
import logging
import numpy as np
import healpy as hp
from astropy.time import Time
from astropy import constants as const
from astropy import units as u
from astropy.coordinates import GCRS, SkyCoord, CartesianRepresentation

from snewpdag.dag import Node, Detector, DetectorDB
from snewpdag.dag.lib import normalize_time, ns_per_second

class TrueTimes(Node):
  def __init__(self, detector_location, detectors, ra, dec, time, **kwargs):
    self.db = DetectorDB(detector_location)
    self.ra = np.radians(ra)
    self.dec = np.radians(dec)
    self.time = Time(time)
    t = self.time.to_value('unix', 'long')
    ti = int(t)
    tf = t - ti
    self.ttuple = (ti, int(tf * ns_per_second))

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

    # generate true times for each detector.
    # given time is when wavefront arrives at Earth origin.
    g = ns_per_second / u.second
    ts = {}
    for dname in self.dets:
      #c = 3.0e8 # m/s
      det = self.db.get(dname)
      pos = det.get_xyz(self.time) # detector in GCRS at given time
      logging.info('pos[{}] = {}'.format(dname, pos))
      logging.info('  sn pos = {}'.format(self.snr))
      dt = - np.dot(det.get_xyz(self.time), self.snr) / const.c # intersect
      dtt = (self.ttuple[0], self.ttuple[1] + dt * g)
      ts[dname] = {
                    'true_t': normalize_time(dtt), # (s, ns)
                  }

    data['truth']['dets'] = ts
    return data

