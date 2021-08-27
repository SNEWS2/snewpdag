"""
NeutrinoArrivalTime: Generate the neutrino arrival time for a list of detectors 

Constructor Arguments:
    detector_list: list of strings, ["first_detector", "second_detector", ...]
                the list of detectors that we want to generate time delay
                options: "HK", "IC", "JUNO", "KM3", "SK"
    detector_location: csv file ('detector_location.csv')

Output added to data: dictionary with key "detector_name" and corresponding arrival time.

"""

import csv
import numpy as np
import random as rm
from datetime import datetime
from snewpdag.dag import Node
from snewpdag.dag import lib

class NeutrinoArrivalTime(Node):
    #Define detector location
    def __init__(self, detector_list, detector_location, **kwargs):
        self.detector_info = {}
        with open(detector_location, 'r') as f:
            detectors = csv.reader(f)
            for detector in detectors:
                name = detector[0]
                if name in detector_list: 
                    lon = np.radians(float(detector[1]))
                    lat = np.radians(float(detector[2]))
                    height = float(detector[3])
                    self.detector_info[name] = [lon, lat, height]
        super().__init__(**kwargs)


    #Randomly generate the direction vector for incoming neutrino flux, using right-ascention(alpha) and declination(delta)
    #costheta gives the polar angle distribution, and delta = pi/2 - polar
    def generate_n(self):
        alpha_deg = rm.uniform(-180,180)
        alpha = np.radians(alpha_deg)
        costheta = rm.uniform(-1,1)  #cos(theta) = sin(delta)

        nx = -np.cos(alpha)*np.sqrt(1-costheta*costheta)
        ny = -np.sin(alpha)*np.sqrt(1-costheta*costheta)
        nz = -costheta  

        source = (nx, ny, nz)
        return source


    #randomly generate a time between 2000-1-1, 00:00 and 2000-12-31, 23:59:59 UTC for SN neutrino signal to arrive on Earth
    #unix time for 2000-1-1, 00:00 is 946713600.0
    def generate_time(self):
        start_unix = 946713600
        random_time = rm.randrange(0, 31536000) #number of second in a year
        s = start_unix + random_time 
        ns = rm.randrange(0,1e9)
        return (s, ns)


    #calculate the distance between the detector and the center of the Earth
    #Input: first_det/second_det are arrays of the form [lon, lat, height], 
    #Default arrival time: (vernal equinox): 2000-03-20, 12:00 PM UTC; its unix time is 953582400.0
    def detector_diff(self, detector, arrival=(953582400, 0)):
        earth = 6.37e6 #m
        ang_rot = 7.29e-5 #radians/s
        ang_sun = 2e-7 #radians/s   2pi/365days

        #take into account the time dependence of longitude  
        #reference: arXiv:1304.5006
        arrival_date = datetime.fromtimestamp(arrival[0])
        decimal = arrival[1]*1e-9
        t_rot = arrival_date.hour*60*60 + arrival_date.minute*60 + arrival_date.second + decimal  #(0 <= t <= 24h)
        t_sun = arrival[0] - 953582400 + decimal #time elapsed after the vernal point when the detector received the SN neutrinos

        lon = detector[0] + ang_rot*t_rot - ang_sun*t_sun - np.pi
        lat = detector[1]
        h = detector[2] 

        #Calculate the displacement vector of the given two detectors
        rx = (earth+h)*np.cos(lon)*np.cos(lat)
        ry = (earth+h)*np.sin(lon)*np.cos(lat)
        rz = (earth+h)*np.sin(lat)

        r = (rx, ry, rz)
        return r


    #calculate the arrival time difference given SN location and the distance of the detector to the center of the Earth
    def time_delay(self, detector_diff, source):
        c = 3e8
        t = np.dot(detector_diff, source)/c
        return t


    #Generate neutrino flux direction and arrival time
    #Calculate the neutrino arrival time of each detector
    def alert(self, data):
        nvec = self.generate_n()
        t = self.generate_time() 
        d = {'sn_direction':nvec,
             'sn_times':{
                'Earth':t
                        }
            }
        for name in self.detector_info:
            detector = self.detector_info[name]
            posdiff = self.detector_diff(detector, t)
            time_delay = self.time_delay(posdiff, nvec) 
            s = t[0]
            ns = t[1]+ round(time_delay*1e9)
            a = (s, ns)
            arrival_time = tuple(lib.normalize_time(a))
            d['sn_times'][name] = arrival_time

        if 'gen' in data:
            data['gen'].update(d)
        else:
            data['gen'] = d
        return True
