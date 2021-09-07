"""
DetectorTime: Look up the detector in gen/sn_times and gen/neutrino_times, and store the values 
              in sn_time and neutrino_time in the payload

Constructor Arguments:
    detector: the name of detector

"""

from snewpdag.dag import Node

class DetectorTime(Node):

    def __init__(self, detector, **kwargs):
        self.detector = detector
        super().__init__(**kwargs)
    
    def alert(self, data):
        true_time = data['gen']['sn_times'][self.detector]
        observed_time = data['gen']['neutrino_times'][self.detector]
        a = {self.detector: true_time}
        b = {self.detector: observed_time}
        if 'sn_time' in data:
            data['sn_time'].update(a)
        else:
            data['sn_time'] = a
        if 'neutrino_time' in data:
            data['neutrino_time'].update(b)
        else:
            data['neutrino_time'] = b
        return True