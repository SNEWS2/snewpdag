"""
Chi2Calculator: generates a skymap of SN direction probabilities

Constructor Arguments:
    detector_list: list of strings, ["first_detector", "second_detector", ...]    \
                the list of detectors that we want to include in the calculations  \
                options: "HK", "IC", "JUNO", "KM3", "SK"                           / same as in NeutrinoArrivalTime
    detector_location: csv file name ('detector_location.csv')                  __/
    output_file: name of file to save .fits map to (e.g. 'output/map.fits')
    DET0: detector with the lowest error (delta_ts are calculated w.r.t. this detector) (e.g. 'SK')
    NSIDE: (int) healpy map parameter, it describes map resolution (32 is a reasonable number)
    add_contours: (bool) (optional argument, default is True) if True than 1-, 2- and 3-sigma countours
                  are rescaled to make them visible (map is no longer a real chi^2 map), otherwise chi^2
                  map without any rescaling is saved

Output:
    It doesn't add anything to data, saves a .fits file to <output_file>
"""

import csv
import numpy as np
import healpy as hp
import math
from scipy.stats import chi2
from datetime import datetime

from snewpdag.dag import Node


class Chi2Calculator(Node):
    def __init__(self, detector_list, detector_location,
                 det0, NSIDE, output_file, **kwargs):
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
        self.precision_matrix = self.generatePrecisionMatrix()
        self.n_dof = len(detector_list) - 3
        self.NSIDE = NSIDE
        self.NPIX = hp.nside2npix(NSIDE)
        self.output_file = output_file

        if 'add_contours' in kwargs:
            self.add_contours = kwargs.pop('add_contours')
        else:
            self.add_contours = True

        super().__init__(**kwargs)

    # Generates precision matrix (inverse of covariance matrix)
    def generatePrecisionMatrix(self):
        sigma_0 = self.d0_info[3]
        n_detectors = len(self.detector_info)
        V = [[sigma_0]*n_detectors for i in range(n_detectors)]
        for i in range(n_detectors):
            det = list(self.detector_info.keys())[i]
            V[i][i] = self.detector_info[det][3]
        return np.linalg.inv(V)

    # Generates unit vector for given lattitude and magnitude,
    # pointing towards sky
    # alpha range is (-pi, pi), delta range is (-pi/2, pi/2)
    def angles_to_unit_vec(self, alpha, delta):
        x = math.cos(alpha)*math.cos(delta)
        y = math.sin(alpha)*math.cos(delta)
        z = math.sin(delta)
        return np.matrix([x, y, z]).getT()

    # For comparing with generator plugin
    def unit_vec_to_angles(self, n):
        delta = math.asin(n[2])
        alpha = math.asin(n[1] / math.cos(delta))
        return -alpha, -delta

    # Calculates detecotr position in cartesian coordinates
    def det_cartesian_position(self, det):
        # Part was copied from NeutrinoArrivalTime
        ang_rot = 7.29e-5  # radians/s
        ang_sun = 2e-7  # radians/s   2pi/365days

        # take into account the time dependence of longitude
        # reference: arXiv:1304.5006
        arrival_date = datetime.fromtimestamp(self.arrival[0])
        decimal = self.arrival[1]*1e-9

        t_rot = arrival_date.hour*60*60\
              + arrival_date.minute*60 + arrival_date.second + decimal

        t_sun = self.arrival[0] - 953582400 + decimal

        lon = det[0] + ang_rot*t_rot - ang_sun*t_sun - np.pi
        lat = det[1]
        r = 6.37e6 + det[2]

        return r*self.angles_to_unit_vec(lon, lat)

    # Calculates time_diff given detector names and supernova location
    def time_diff(self, det1, det2, n):
        det1_pos = self.det_cartesian_position(det1)
        det2_pos = self.det_cartesian_position(det2)
        return float((det1_pos - det2_pos).getT() @ n)/3.0e8

    # Calculates chi2 for given vector d
    def chi2(self, d):
        return (d.getT() @ (self.precision_matrix @ d))

    # Calculates vector d given supernova position and t_m
    def d_vec(self, n, dt_i):
        n_detectors = len(self.detector_info)
        d = [0]*n_detectors

        for i in range(n_detectors):
            det = list(self.detector_info.keys())[i]
            det0 = self.d0_info[-1]
            d[i] = dt_i[det][0] + dt_i[det][1] / 1e9 \
                - dt_i[det0][0] - dt_i[det0][1] / 1e9

            d[i] = d[i] - self.detector_info[det][4] + self.d0_info[4]

            d[i] -= self.time_diff(self.detector_info[det], self.d0_info, n)

        return np.matrix(d).getT()

    # Estimates the SN direction,
    # could be used for debugging purposes
    def calculate_real_n(self, dt_i):
        chi2_min = 1e12

        for i in range(self.NPIX):
            delta, alpha = hp.pixelfunc.pix2ang(self.NSIDE, i)
            delta = delta - math.pi/2
            alpha = alpha - math.pi

            n_pointing = -1*self.angles_to_unit_vec(alpha, delta)
            chi2_at_n = self.chi2(self.d_vec(n_pointing, dt_i))
            if chi2_at_n < chi2_min:
                chi2_min = chi2_at_n
                n = n_pointing
        return n

    # Puts contours on a map
    def draw_contours(self, map):
        sigma1 = chi2.ppf(0.683, self.n_dof)
        sigma2 = chi2.ppf(0.955, self.n_dof)
        sigma3 = chi2.ppf(0.997, self.n_dof)

        # Some arbitrary numbers that make good contrast
        c1 = 10  # map.max()
        c2 = 8  # (map.max() + map.min())/3
        c3 = 7  # (map.max() + map.min())*2/3
        out = 0  # map.min()

        for i in range(len(map)):
            if map[i] < sigma1:
                map[i] = c1
            elif map[i] < sigma2:
                map[i] = c2
            elif map[i] < sigma3:
                map[i] = c3
            else:
                map[i] = out

        return map

    # Generates chi2 map
    def generate_map(self, dt_i):
        map = np.zeros(self.NPIX)

        for i in range(self.NPIX):
            delta, alpha = hp.pixelfunc.pix2ang(self.NSIDE, i)
            delta = delta - math.pi/2
            alpha = alpha - math.pi

            n_pointing = -1*self.angles_to_unit_vec(alpha, delta)
            map[i] = self.chi2(self.d_vec(n_pointing, dt_i))

        return map

    def alert(self, data):
        dt_i = data['gen']['sn_times']
        self.arrival = dt_i['Earth']

        map = self.generate_map(dt_i)

        if self.add_contours:
            map = self.draw_contours(map)

        hp.write_map(self.output_file, map, overwrite=True)

        return True
