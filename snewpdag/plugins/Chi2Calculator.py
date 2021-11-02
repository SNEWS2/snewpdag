"""
Chi2Calculator: generates a skymap of SN direction probabilities

Constructor Arguments:                                                          __
    detector_list: list of strings, ["first_detector", "second_detector", ...]    \
                the list of detectors that we want to include in the calculations  \
                options: "HK", "IC", "JUNO", "KM3", "SK"                           / same as in NeutrinoArrivalTime
    detector_location: csv file name ('detector_location.csv')                  __/
    NSIDE: (int) healpy map parameter, it describes map resolution (32 is a reasonable number)

Output:
    adds hp map (np.array) in nested ordering as 'chi2' and number of DOF (int) as 'ndof' to data
"""

import csv
import logging
import numpy as np
import healpy as hp
from numpy.core.numeric import Inf
from scipy.stats import chi2
from datetime import datetime

from snewpdag.dag import Node

class Chi2Calculator(Node):
    def __init__(self, detector_list, detector_location,
                NSIDE, **kwargs):
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
                self.detector_info[name] = [lon, lat, height, sigma, bias]
        self.NSIDE = NSIDE
        self.NPIX = hp.nside2npix(NSIDE)
        self.map = {}

        self.measured_times = {}
        for detector in detector_list:
            self.measured_times[detector] = None

        super().__init__(**kwargs)

    # Makes handling times easier
    def get_time_dicts(self):
        measured = dict(filter(lambda element: element[1] != None, self.measured_times.items()))

        det_0 = ""
        sigma_0 = Inf

        for det in measured:
            if self.detector_info[det][3] < sigma_0:
                sigma_0 = self.detector_info[det][3]
                det_0 = det
        det0_time = measured.pop(det_0)

        measured_det_info = dict(filter(lambda element: element[0] in measured.keys(), self.detector_info.items()))
        det0_info = self.detector_info[det_0]

        return measured, measured_det_info, det0_time, det0_info

    # Generates precision matrix (inverse of covariance matrix)
    def generatePrecisionMatrix(self, measured_det_info, det0_info):

        n_det = len(measured_det_info)
        sigma_0 = det0_info[3]
        V = np.zeros((n_det, n_det))

        for i in range(n_det):
            for j in range(n_det):
                if i == j:
                    det = list(measured_det_info.keys())[i]
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
    def d_vec(self, n, measured, measured_det_info, det0_time, det0_info):
        n_detectors = len(measured)
        d = np.zeros(n_detectors)

        for i in range(n_detectors):
            det = list(measured.keys())[i]
            
            d[i] = measured[det][0] + measured[det][1] / 1e9 \
                 - det0_time[0] - det0_time[1] / 1e9

            d[i] = d[i] - measured_det_info[det][4] + det0_info[4]
            d[i] -= self.time_diff(measured_det_info[det], det0_info, n)

        return np.matrix(d).getT()

    # Generates chi2 map
    def generate_map(self, measured, measured_det_info, det0_time, det0_info):
        map = np.zeros(self.NPIX)

        for i in range(self.NPIX):
            delta, alpha = hp.pixelfunc.pix2ang(self.NSIDE, i, nest=True)

            delta -= np.pi/2
            alpha -= np.pi

            n_pointing = -1*self.angles_to_unit_vec(alpha, delta)
            map[i] = self.chi2(self.d_vec(n_pointing, measured, measured_det_info, det0_time, det0_info))

        chi2_min = map.min()
        for i in range(self.NPIX):
            map[i] -= chi2_min

        return map

    # calculate skymap given two or more detectors data
    def calculate_skymap(self, data):
        time = data['neutrino_time']
        if 'detector_id' in data:
            det = data['detector_id']
        else:
            # if detector_id is not in the payload, then assume we are running a MC trial
            # search the name of the detector in data['gen']['neutrino_times']
            #det = self.last_source
            for det_name, nu_time in data['gen']['neutrino_times'].items():
                if nu_time == time:
                    det = det_name

        self.measured_times[det] = time

        self.map[self.last_source] = data.copy()
        self.map[self.last_source]['history'] = data['history'].copy()
        self.map[self.last_source]['valid'] = True

        measured, measured_det_info, det0_time, det0_info = self.get_time_dicts()

        sum_s = det0_time[0]
        sum_ns = det0_time[1]
        for s, ns in measured.values():
            sum_s += s
            sum_ns += ns
        self.arrival = (sum_s / (len(measured) + 1), sum_ns / (len(measured) + 1))


        # Takes only the detectors for which time has been measured
        if len(measured) < 1:
            return False
        n_of_detectors = len(measured) + 1  #rdallava: +1 accounting for the fact that python start counting from 0
        self.precision_matrix = self.generatePrecisionMatrix(measured_det_info, det0_info)
        map = self.generate_map(measured, measured_det_info, det0_time, det0_info)


        data['map'] = map
        data['n_of_detectors'] = n_of_detectors

        hlist = []
        for k in self.map:
            if self.map[k]['valid']:
                hlist.append(self.map[k]['history'])
        data['history'].combine(hlist)
        return data


    def alert(self, data):
        data = self.calculate_skymap(data)
        logging.warning(data)
        return data

    def revoke(self, data):
        time = data['neutrino_time']
        if 'detector_id' in data:
            det = data['detector_id']
        else:
            det = self.last_source

        # Check if the time has changed, otherwise there is no point in recalculating the skymap
        if self.measured_times[det] == time:
            return False

        data = self.calculate_skymap(data)
        return data


