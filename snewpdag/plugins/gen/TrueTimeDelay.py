"""
TrueTimeDelay: Calculate the true time delay of the neutrino arrival between two detectors
by randomly generate a neutrino directional vector and a arrival time 

Constructor Arguments:
    first_det: string, "first detector name"
                options: "ARCA", "IC", "SK", "HK", "JUNO"
    second_det: string, "second detector name"
                options: "ARCA", "IC", "SK", "HK", "JUNO"
    detector_location: csv file ('detector_location.csv')

Output added to data: gen_to (true time delay)

"""

import logging
import csv
import time
import numpy as np
import random as rm
from datetime import datetime
from snewpdag.dag import Node

class TrueTimeDelay():

    #Define detector location
    def __init__(self, first_det, second_det, detector_location, **kwargs):
        self.first_det = first_det
        self.second_det = second_det

        with open(detector_location, 'r') as f:
            detectors = csv.reader(f)
            for detector in detectors:
                if detector[0] == first_det: 
                    first_lon = np.radians(float(detector[1]))
                    first_lat = np.radians(float(detector[2]))
                    first_height = float(detector[3])
                    self.first_det_info = [first_lon, first_lat, first_height]
                if detector[0] == second_det:
                    second_lon = np.radians(float(detector[1]))
                    second_lat = np.radians(float(detector[2]))
                    second_height = float(detector[3])
                    self.second_det_info = [second_lon, second_lat, second_height]

        super().__init__(**kwargs)


    #Randomly generate the direction vector for incoming neutrino flux

    def generate_n(self):

    #randomly generate a SN coordinate in the sky in terms of right-ascention alpha (-180° - 180°)
    #and declination delta (-90° - 90°)
        alpha_deg = rm.uniform(-180,180)
        delta_deg = rm.uniform(-90,90)
    
        alpha = np.radians(alpha_deg)
        delta = np.radians(delta_deg)
        
        nx = -np.cos(alpha)*np.cos(delta)
        ny = -np.sin(alpha)*np.cos(delta)
        nz = -np.sin(delta)
        
        source = np.array([nx, ny, nz])
        return source


    #randomly generate a time between 2000-1-1, 00:00 and 2000-12-31, 23:59:59 UTC for SN neutrino signal to arrive on Earth
    #base time (vernal equinox): 2000-03-20, 12:00 PM UTC
    def generate_time(self):
        d = rm.randrange(0, 31536000)
        start_range = datetime(2000,1,1,0,0,0)
        start_unix = time.mktime(start_range.timetuple())
        random_unix = d + start_unix 
        generated_time = datetime.fromtimestamp(random_unix)
        return generated_time


    #calculate the distance between two detectors
    #Input: longitude, latitude, height(optional)
    def detector_diff(self, first_det, second_det, arrival=datetime(2000,3,20,12)):
        earth = 6.37e6 #m
        ang_rot = 7.29e-5 #radians/s
        ang_sun = 2e-7 #radians/s   2pi/365days
        
        #take into account the time dependence of longitude  
        #reference: arXiv:1304.5006
        t = arrival.hour*60*60 + arrival.minute*60 + arrival.second  #(0 <= t <= 24h)
        T = (arrival - datetime(2000,3,20,12)).total_seconds() #time elapsed after the vernal point when the detector received the SN neutrinos
        
        first_lon = first_det[0] + ang_rot*t - ang_sun*T - np.pi
        first_lat = first_det[1]
        second_lon = second_det[0] + ang_rot*t - ang_sun*T - np.pi
        second_lat = second_det[1]
        
        #If the height of detector is not given, assume at sea level
        if len(first_det)>2:
            first_h = first_det[2]
        else:
            first_h = 0
            
        if len(second_det)>2:
            second_h = second_det[2]
        else:
            second_h = 0
        
        first_rx = (earth+first_h)*np.cos(first_lon)*np.cos(first_lat)
        first_ry = (earth+first_h)*np.sin(first_lon)*np.cos(first_lat)
        first_rz = (earth+first_h)*np.sin(first_lat)

        second_rx = (earth+second_h)*np.cos(second_lon)*np.cos(second_lat)
        second_ry = (earth+second_h)*np.sin(second_lon)*np.cos(second_lat)
        second_rz = (earth+second_h)*np.sin(second_lat)

        first_r = np.array([first_rx, first_ry, first_rz])
        second_r = np.array([second_rx, second_ry, second_rz])

        diff_r = np.subtract(first_r, second_r)
        return diff_r


    #calculate the arrival time difference given SN location and distance
    #between two detectors
    def time_delay(self, detector_diff, source):
        c = 3e8
        t = np.dot(detector_diff, source)/c
        return t


    def alert(self, data):
        nvec = self.generate_n()
        t = self.generate_time() 
        posdiff = self.detector_diff(self.first_det_info, self.second_det_info, t)
        truedelay = self.time_delay(nvec, posdiff)
        print(truedelay)
        detector_pair = self.first_det + ', ' + self.second_det
        d = {detector_pair: truedelay}
        data.update(d)
        return True
