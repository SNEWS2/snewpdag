"""
AddErrors: Adds detector biases and random gaussian errors to the NeutrinoArrivalTime plugin output

Constructor Arguments:
    detector_list, detector_location -> same as for NeutrinoArrivalTime

Output:
    data['gen']['det_times'] dict containing detector times with added errors
    e.g. {'SK': <float>, 'IC': <float>}

"""

import csv
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag import lib


class AddErrors(Node):
    def __init__(self, detector_list, detector_location, **kwargs):
        self.detector_error_info = {}
        with open(detector_location, 'r') as f:
            detectors = csv.reader(f)
            for detector in detectors:
                name = detector[0]
                if name not in detector_list:
                    continue
                sigma = float(detector[4])
                bias = float(detector[5])
                self.detector_error_info[name] = [sigma, bias]
        super().__init__(**kwargs)

    def alert(self, data):
        arrival_times = data['gen']['sn_times']

        det_times = {}
        for name in arrival_times:
            if name == 'Earth':
                continue
            else:
                time = arrival_times[name]
                sigma = self.detector_error_info[name][0]
                bias = self.detector_error_info[name][1]

                det_times.update(
                    {name: np.random.normal(loc=bias, scale=sigma)}
                    )

        data['gen']['det_times'] = det_times

        return True
