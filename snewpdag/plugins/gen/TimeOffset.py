"""
TimeOffset: Add time offset to true arrival time for each detector 

Constructor Arguments:
    detector_location: csv file ('detector_location.csv')

Output added to data: update the offsetted time to "gen_dts"

"""


import csv
import random as rm
import logging
from snewpdag.dag import Node
from snewpdag.dag import lib

class TimeOffset(Node):
    
    #Specify arrivial time uncertainties (s)
    def __init__(self, detector_location, **kwargs):
        self.detector_offset = {}
        with open(detector_location, 'r') as f:
            detectors = csv.reader(f)
            next(f) #skip the heading 
            for detector in detectors:
                name = detector[0]
                self.detector_offset[name] = [float(detector[4]), float(detector[5])]
        super().__init__(**kwargs)
        
    #Add time offset to true arrival time and update payload
    def alert(self, data):
        for item in data['gen']['sn_times'].items():
            detector = item[0]
            true_arrival = item[1]
            
            #skip reference time
            if detector == 'Earth':
                continue
            #skip iteration if missing reoltuion parameter for one detector
            if detector not in self.detector_offset.keys():
                logging.error('Do not have a resolution parameter for detector {}.'.format(detector))
                continue

            uncertainty = self.detector_offset[detector][0]
            bias = self.detector_offset[detector][1]
            
            offsetted_s = true_arrival[0]
            offset = round(rm.gauss(bias*1e9, uncertainty*1e9))
            offsetted_ns = true_arrival[1] + offset 

            a = (offsetted_s, offsetted_ns)
            offsetted_time = tuple(lib.normalize_time(a))
            d = {detector:offsetted_time}
            if 'neutrino_times' in data['gen']:
                data['gen']['neutrino_times'].update(d)
            else:
                data['gen']['neutrino_times'] = d
        return True
