"""
DiffPoint: generate a skymap of SN direction chi2's
  based on Wiktor Jasniak's Chi2Calculation
"""
import csv
import logging
import numpy as np
import healpy as hp
from datetime import datetime

from snewpdag.dag import Node

class DiffPoint(Node):
  def __init__(self, detector_pairs, detector_location, nside, **kwargs):
    self.pairs = []
    for p in detector_pairs:
      self.pairs.append(set(p))
    dlist = []
    for p in self.pairs:
      dlist.extend(p) # add elements of pairs to dlist
    self.dets = set(dlist) # unordered, unique elements
    self.detector_info = {}
    with open(detector_location, 'r') as f:
      detectors = csv.reader(f)
      for detector in detectors:
        name = detector[0]
        if name in self.dets:
          lon = np.radians(float(detector[1]))
          lat = np.radians(float(detector[2]))
          height = float(detector[3])
          sigma = float(detector[4])
          bias = float(detector[5])
          self.detector_info[name] = [lon, lat, height, sigma, bias]
    self.nside = nside
    self.npix = hp.nside2npix(nside)
    self.dts = {}
    self.min_dts = 3
    super().__init__(**kwargs)


  def angles_to_unit_vec(self, lon, lat):
    """
    Calculates unit vector for given lattitude and longitude,
    pointing towards sky
    alpha range is (-pi, pi), delta range is (-pi/2, pi/2)
    """
    x = np.cos(lon)*np.cos(lat)
    y = np.sin(lon)*np.cos(lat)
    z = np.sin(lat)
    return np.matrix([x, y, z]).getT()

  def det_cartesian_position(self, det):
    """
    Calculates detector position in cartesian coordinates
    """
    ang_rot = 7.29e-5  # radians/s
    ang_sun = 2e-7  # radians/s   2pi/365days

    # take into account the time dependence of longitude
    # reference: arXiv:1304.5006
    arrival_date = datetime.fromtimestamp(self.arrival[0])
    decimal = self.arrival[1]*1e-9

    t_rot = arrival_date.hour*60*60 \
          + arrival_date.minute*60 + arrival_date.second + decimal

    t_sun = self.arrival[0] - 953582400 + decimal

    lon = det[0] + ang_rot*t_rot - ang_sun*t_sun - np.pi
    lat = det[1]
    r = 6.37e6 + det[2]

    return r*self.angles_to_unit_vec(lon, lat)

  def time_diff(self, det1, det2, n):
    """
    Calculates time_diff given detector names and supernova location
    """
    c = 3.0e8  # speed of light /m*s^-1
    det1_pos = self.det_cartesian_position(det1)
    det2_pos = self.det_cartesian_position(det2)
    diff = float((det1_pos - det2_pos).getT() @ n)/c
    return diff

  def chi2(self, d):
    """
    calculate chi2 for a given difference vector d
    """
    return d.getT() @ (self.precision_matrix @ d)

  def reevaluate(self):
    """
    Reevaluate direction based on available time differences
    """
    m = np.zeros(self.npix)
    for i in range(self.npix):
      delta, alpha = np.pixelfunc.pix2ang(self.nside, i, nest=True)
      delta -= 0.5 * np.pi
      alpha -= np.pi
      n_pointing = - self.angles_to_unit_vec(alpha, delta)
      m[i] = self.chi2(self.d_vec(n_pointing))

    chi2_min = m.min()
    m -= chi2_min
    data['map'] = m
    data['ndof'] = 2

  def alert(self, data):
    sources = set(data['detector_ids'])
    if sources in self.pairs:
      self.dts[sources] = data['dt']
      if len(self.dts) >= self.min_dts:
        return self.reevaluate()
      else:
        return False

  def revoke(self, data):
    sources = set(data['detector_ids'])
    if sources in self.pairs:
      self.dts.pop(sources)
      if len(self.dts) >= self.min_dts:
        return self.reevaluate()
      else if len(self.dts) == self.min_dts - 1:
        return True # just fell below min_dts threshold; forward revoke

