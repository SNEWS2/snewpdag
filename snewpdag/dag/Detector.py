"""
Detector - detector instance
"""
import numpy as np
from astropy.coordinates import EarthLocation
from astropy.time import Time

class Detector:
  def __init__(self, name, lon, lat, height, sigma, bias):
    self.name = name
    self.lon = lon # degrees
    self.lat = lat # degrees
    self.height = height # [m]
    self.sigma = sigma # time resolution [s]
    self.bias = bias # time bias [s], observed - true
    delta = np.radians(90.0 - lat)
    alpha = np.radians(lon)
    self.r = np.array([ np.sin(delta) * np.cos(alpha),
                        np.sin(delta) * np.sin(alpha),
                        np.cos(delta) ])
    self.loc = EarthLocation(lon=lon, lat=lat)

  def get_gcrs(self, obstime):
    #k = EarthLocation.of_site('keck')
    t = Time(obstime) # make sure it's in astropy Time form
    g = self.loc.get_gcrs(obstime=t) # g.ra and g.dec
    return g

  def get_xyz(self, obstime):
    g = self.get_gcrs(obstime)
    radius = np.sqrt(self.loc.x**2 + self.loc.y**2 + self.loc.z**2)
    codelta = np.radians(g.dec)
    alpha = np.radians(g.ra)
    sphi = np.sin(alpha)
    cphi = np.cos(alpha)
    ctheta = np.sin(codelta)
    stheta = np.cos(codelta)
    return radius * np.array([ stheta * cphi, stheta * sphi, ctheta ])

