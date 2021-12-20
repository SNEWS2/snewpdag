"""
DetectorDB - detector database
"""
import csv
import logging

from . import Detector

class DetectorDB:

  dets = {}
  files = []

  def __init__(self, filename):
    if len(DetectorDB.dets) > 0 and filename in DetectorDB.files:
      # check if already read in this file
      return
    logging.info('Read detector database file {}'.format(filename))
    DetectorDB.files.append(filename)
    with open(filename, 'r') as f:
      cr = csv.reader(f)
      for det in cr:
        name = det[0]
        if len(name) > 0:
          lon = float(det[1])
          lat = float(det[2])
          height = float(det[3])
          sigma = float(det[4])
          bias = float(det[5])
          d = Detector(name, lon, lat, height, sigma, bias)
          DetectorDB.dets[name] = d

  def has(self, name):
    return name in DetectorDB.dets

  def get(self, name):
    if self.has(name):
      return DetectorDB.dets[name]
    else:
      return None

