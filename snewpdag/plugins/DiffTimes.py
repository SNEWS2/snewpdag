"""
DiffTimes - calculate dt's from a list of detector names and timestamps.

Arguments:
  detector_location: filename of detector database for DetectorDB

Input payload:
  detector_names:  list of detector names
  neutrino_times:  list of timestamps corresponding to detector_names

Output payload:
  dts: a dictionary of time differences. Keys are of form (det1,det2),
    a list or tuple of detector names (as given in DetectorDB).  The values
    are themselves dictionaries with the following keys:
    required:
      dt: t1-t2.
      t1: burst time of det1.
      t2: burst time of det2.
    optional (values derived from DetectorDB if not present):
      bias: bias in dt in seconds, given as bias1-bias2.
      var: variance (stddev**2) of dt in seconds.
      dsig1: (d(dt)/dt1) * sigma1, in seconds, for covariance calculation.
      dsig2: (d(dt)/dt2) * sigma2, in seconds, for covariance calculation.
"""
import logging
import numpy as np

from snewpdag.dag import Node, Detector, DetectorDB
from astropy.time import Time

class DiffTimes(Node):
  def __init__(self, detector_location, **kwargs):
    self.db = DetectorDB(detector_location)
    super().__init__(**kwargs)

  def alert(self, data):
    if 'detector_names' in data and 'neutrino_times' in data:

      # get timestamps
      ts = []
      bias = []
      sigma = []
      ndet = len(data['detector_names'])
      for index in range(ndet):
        dn = data['detector_names'][index]
        det = self.db.get(dn)
        bias.append(det.bias)
        sigma.append(det.sigma)
        ts.append(Time(data['neutrino_times'][index]).to_value('unix', 'long'))

      # find a detector with smallest sigma
      ibest = np.argmin(sigma)

      # form time differences with first detector listed (for now)
      dts = {}
      dn0 = data['detector_names'][ibest]
      for index in range(ndet):
        if index == ibest:
          continue
        dn1 = data['detector_names'][index]
        dts[(dn0,dn1)] = {
                           'dt': ts[ibest] - ts[index],
                           't1': ts[ibest],
                           't2': ts[index],
                           'bias': bias[ibest] - bias[index],
                           'var': sigma[ibest]**2 + sigma[index]**2,
                           'dsig1': sigma[ibest],
                           'dsig2': - sigma[index],
                         }
        data['dts'] = dts

      return data
    else:
      return False

