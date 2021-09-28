"""
DetectorTime: Look up the detector in gen/sn_times and gen/neutrino_times, and store the values 
              in sn_time and neutrino_time in the payload

Constructor Arguments:
    detector: the name of detector

"""

import logging
from snewpdag.dag import Node

class DetectorTime(Node):

    def __init__(self, detector, **kwargs):
        self.detector = detector
        super().__init__(**kwargs)
    
    def alert(self, data):
        if self.detector not in data['gen']['sn_times']:
            logging.error("{} is not in the payload.".format(self.detector))
            return True
        true_time = data['gen']['sn_times'][self.detector]
        observed_time = data['gen']['neutrino_times'][self.detector]
        data['sn_time'] = true_time
        data['neutrino_time'] = observed_time
        return True
