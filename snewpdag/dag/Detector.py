"""
Detector - detector instance
"""
import numpy as np

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

