"""
TrueTimeDelay: Calculate the true time delay of the neutrino arrival between two detectors
by randomly generate a neutrino directional vector and a arrival time 

Constructor Arguments:
    first_det: string, "first detector name"
                options: "ARCA", "IC", "SK", "HK", "JUNO"
    second_det: string, "second detector name"
                options: "ARCA", "IC", "SK", "HK", "JUNO"

Output added to data: gen_to (true time delay)

"""

import logging
import numpy as np
import random as rm
from datetime import datetime
from snewpdag.dag import Node

class TrueTimeDelay(Node):

    #Input detector coordinate information 
    lonKM3 = np.radians(16.+6./60.) #Letter Of Intent
    latKM3 = np.radians(36.+16./60.) #Letter Of Intent  
    lonIC = -np.radians(63+27/60.+11./3600.) #wiki
    latIC = -np.radians(89.+59./60.+24./3600.) #wiki
    lonSK = np.radians(137. + 18./60. + 37.1/3600.) #http://www-sk.icrr.u-tokyo.ac.jp/~masato_s/class/sk-detector.pdf
    latSK = np.radians(36. + 25./60. + 32.6/3600.)  #http://www-sk.icrr.u-tokyo.ac.jp/~masato_s/class/sk-detector.pdf
    lonHK = np.radians(137. + 18./60. + 49.137/3600.) #https://arxiv.org/pdf/1805.04163.pdf 
    latHK = np.radians(36. + 21./60. + 20.105/3600.)  #https://arxiv.org/pdf/1805.04163.pdf 
    lonJUNO = np.radians(112.51867) #arXiv:1909.03151
    latJUNO = np.radians(22.11827) #arXiv:1909.03151

    det_coord = {
            "ARCA": [lonKM3,latKM3],
            "IC": [lonIC,latIC],
            "SK": [lonSK,latSK],
            "HK": [lonHK,latHK],
            "JUNO": [lonJUNO,latJUNO]
            }

    def __init__(self, first_det, second_det, **kwargs):
        self.first_det = first_det
        self.second_det = second_det
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


    #randomly generate a time for SN neutrino signal to arrive on Earth
    #base time: 2000-03-20, 12:00 PM UTC
    def generate_time(self):
        month = rm.randrange(1,13)
        if month in [1,3,5,7,8,10,12]:
            day = rm.randrange(1,32)
        elif month == 2:
            day = rm.randrange(1,29)
        else:
            day = rm.randrange(1,31)
        hour = rm.randrange(0,24)
        minute = rm.randrange(0,60)
        second = rm.randrange(0,60)
        if month <3:
            year = 2001
        else:
            year = 2000
        return datetime(year, month, day, hour, minute, second)


    #calculate the distance between two detectors
    #Input: longitude, latitude, height(optional)
    def detector_diff(self, first_det, second_det, arrival=datetime(2000,3,20,12)):
        earth = 6.37e6 #m
        ang_rot = 7.29e-5 #radians/s
        ang_sun = 2e-7 #radians/s   2pi/365days
        
        #take into account the time dependence of longitude  
        #reference: arXiv:1304.5006
        t = arrival.hour*60*60 + arrival.minute*60 + arrival.second
        T = (arrival - datetime(2000,3,20,12)).total_seconds()
        
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
        time = self.generate_time()
        first_det = self.det_coord[self.first_det]
        second_det = self.det_coord[self.second_det]
        posdiff = self.detector_diff(first_det, second_det, time)
        truedelay = self.time_delay(nvec, posdiff)
        d = {'gen_t0': truedelay}
        data.update(d)
        return True
