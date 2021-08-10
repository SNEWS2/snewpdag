"""
Offset: Add time offset to true arrival time for each detector 

Constructor Arguments:
    detector_list: list of strings, ["first_detector", "second_detector", ...]
                the list of detectors that we want to generate time delay
                options: "HK", "IC", "JUNO", "KM3", "SK"

Output added to data: update the offsetted time to "gen_dts"

"""


import random as rm
from snewpdag.dag import Node

class Offset(Node):
    
    #arrivial time uncertainties (s)
    detector_offset = {'SK':0.0009,
                       'JUNO':0.0012,
                       'IC':0.001,
                       'HK':0.0001, #placeholder
                       'KM3':0.0001 #placeholder
    }
    
    def __init__(self, detector_list, **kwargs):
        self.detector_list = detector_list
        super().__init__(**kwargs)
        
    #Add time offset to true arrival time and update payload
    def alert(self, data):
        for detector in self.detector_list:
            true_arrival = data['gen_dts'][detector]
            offset = self.detector_offset[detector]
            offsetted_time = rm.gauss(true_arrival, offset)
            d = {detector:offsetted_time}
            data['gen_dts'].update(d)
        return data
