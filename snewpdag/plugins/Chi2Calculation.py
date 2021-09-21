"""
Chi2Calculator: generates a skymap of SN direction probabilities

Constructor Arguments:
    detector_list: list of strings, ["first_detector", "second_detector", ...]
                the list of detectors that we want to include in the calculations
                options: "HK", "IC", "JUNO", "KM3", "SK"
    detector_location: csv file name ('detector_location.csv')
    DET0: detector with the lowest error (delta_ts are calculated w.r.t. this detector) (e.g. 'SK')
    NSIDE: (int) healpy map parameter, it describes map resolution (32 is a reasonable number)

Output:
    adds hp map (np.array) in nested ordering as 'chi2' and number of DOF (int) as 'ndof' to data
"""

import csv
import logging
import numpy as np
import healpy as hp
from scipy.stats import chi2
from datetime import datetime

from snewpdag.dag import Node


class Chi2Calculator(Node):
    def __init__(self, detector_list, detector_location,
                 det0, NSIDE, **kwargs):
        self.detector_info = {}
        with open(detector_location, 'r') as f:
            detectors = csv.reader(f)
            for detector in detectors:
                name = detector[0]
                if name not in detector_list:
                    continue
                lon = np.radians(float(detector[1]))
                lat = np.radians(float(detector[2]))
                height = float(detector[3])
                sigma = float(detector[4])
                bias = float(detector[5])
                if name == det0:
                    self.d0_info = [
                        lon, lat, height, sigma, bias, name]
                else:
                    self.detector_info[name] = [
                        lon, lat, height, sigma, bias]
        self.NSIDE = NSIDE
        self.NPIX = hp.nside2npix(NSIDE)
        self.precision_matrix = self.generatePrecisionMatrix()
        self.ndof = len(detector_list) - 3

        super().__init__(**kwargs)

    # Generates precision matrix (inverse of covariance matrix)
    def generatePrecisionMatrix(self):
        n_detectors = len(self.detector_info)
        sigma_0 = self.d0_info[3]
        V = np.zeros((n_detectors, n_detectors))
        for i in range(n_detectors):
            for j in range(n_detectors):
                if i == j:
                    det = list(self.detector_info.keys())[i]
                    V[i][j] = sigma_0**2 + self.detector_info[det][3]**2
                else:
                    V[i][j] = sigma_0**2
        return np.linalg.inv(V)

    # Generates unit vector for given lattitude and longnitude,
    # pointing towards sky
    # alpha range is (-pi, pi), delta range is (-pi/2, pi/2)
    def angles_to_unit_vec(self, lon, lat):
        x = np.cos(lon)*np.cos(lat)
        y = np.sin(lon)*np.cos(lat)
        z = np.sin(lat)
        return np.matrix([x, y, z]).getT()

    # Calculates detecotr position in cartesian coordinates
    def det_cartesian_position(self, det):
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

    # Calculates time_diff given detector names and supernova location
    def time_diff(self, det1, det2, n):
        c = 3.0e8  # speed of light /m*s^-1

        det1_pos = self.det_cartesian_position(det1)
        det2_pos = self.det_cartesian_position(det2)

        diff = float((det1_pos - det2_pos).getT() @ n)/c

        return diff

    # Calculates chi2 for given vector d
    def chi2(self, d):
        return (d.getT() @ (self.precision_matrix @ d))

    # Calculates vector d given supernova position and time differences
    def d_vec(self, n, dt_i):
        n_detectors = len(self.detector_info)
        d = np.zeros(n_detectors)

        for i in range(n_detectors):
            det = list(self.detector_info.keys())[i]
            det0 = self.d0_info[-1]
            d[i] = dt_i[det][0] + dt_i[det][1] / 1e9 \
                 - dt_i[det0][0] - dt_i[det0][1] / 1e9

            d[i] = d[i] - self.detector_info[det][4] + self.d0_info[4]
            d[i] -= self.time_diff(self.detector_info[det], self.d0_info, n)

        return np.matrix(d).getT()

    # Generates chi2 map
    def generate_map(self, dt_i):
        map = np.zeros(self.NPIX)

        for i in range(self.NPIX):
            delta, alpha = hp.pixelfunc.pix2ang(self.NSIDE, i, nest=True, lonlat=True)

            n_pointing = -1*self.angles_to_unit_vec(alpha, delta)
            map[i] = self.chi2(self.d_vec(n_pointing, dt_i))

        chi2_min = map.min()
        for i in range(self.NPIX):
            map[i] -= chi2_min

        return map

    def alert(self, data):
        if self.ndof < 1:
            logging.error("Not enough data for chi2 map calculation")
            return False

        dt_i = data['gen']['neutrino_times']
        self.arrival = data['gen']['sn_times']['Earth']

        map = self.generate_map(dt_i)

        data['chi2'] = map
        data['ndof'] = self.ndof

        return True
