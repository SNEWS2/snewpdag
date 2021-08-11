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

class TimeOffset(Node):
    
    #Specify arrivial time uncertainties (s)
    def __init__(self, detector_location, **kwargs):
        self.detector_offset = {}
        with open(detector_location, 'r') as f:
            detectors = csv.reader(f)
            next(f) #skip the heading 
            for detector in detectors:
                name = detector[0]
                self.detector_offset[name] = float(detector[4])
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

            offset = self.detector_offset[detector]
            offsetted_s = true_arrival[0]
            offsetted_ns = round(rm.gauss(true_arrival[1], offset*1e9))

            #Consider the case when go over/below the 1s boundary 
            if len(str(offsetted_ns)) > 9:
                #if there is a gaussian noise larger than one second, take only the ns part
                if int(str(offsetted_ns)[0:-9]) > 1 or int(str(offsetted_ns)[0:-9]) < -1:
                    offsetted_s = true_arrival[0]
                    if offsetted_ns < 0:
                        offsetted_ns = int(1e9) + int(str(offsetted_ns)[-9:])
                    else:
                        offsetted_ns = int(str(offsetted_ns)[-9:])
                    logging.warning('Detector {} has a unusally large offset: more than one second.'.format(detector))
                else:
                    offsetted_s = true_arrival[0] + int(str(offsetted_ns)[0:-9])
                    offsetted_ns = int(str(offsetted_ns)[-9:])
            elif offsetted_ns < 0:
                offsetted_s = true_arrival[0] -1
                offsetted_ns = int(1e9) + offsetted_ns
            else:
                pass
                    
            d = {detector:(offsetted_s, offsetted_ns)}
            data['gen']['sn_times'].update(d)
        return True
