"""
DeltatCalculator: compute the time difference between the observed t0s
                    from the data[neutrino_time] field of two detectors.

Output:
    Time difference between the respective t0s, (s,ns)
"""

import logging
import numpy as np
from snewpdag.dag import Node, lib

class DeltaTCalculator(Node):
        def __init__(self, **kwargs):
            self.valid = [False] * 10  # flags indicating valid data from sources
            self.t = [None] * 10  # observed first nu event time for each detector
            self.h = [0.0] * 10  # histories from each source
            self.dets_names = [None] * 10
            self.dets_nu_times = [0.0] * 10
           # self.uncertainties = [0.0] * 10  # time uncertainties for each source
           # if kwargs.pop('detector_location_file'):
           #     self.db = DetectorDB(kwargs.pop('detector_location_file'))
            super().__init__(**kwargs)

        def alert(self, data):
            index = self.last_watch_index()
            if index < 0:
                source = self.last_source
                logging.error("[{}] Unrecognized source {}".format(self.name, source))
                return False

            time = self.t[index]
            self.t[index] = data.get('neutrino_time')
            for det_name, value in data['gen']['neutrino_times'].items():
                if value == self.t[index]:
                    #det = self.db.get(det_name)
                    #det_uncertainty = det.sigma
                    #self.uncertainties[index] = det_uncertainty
                    self.dets_names[index] = det_name
                    self.dets_nu_times[index] = value

            if self.t[index] != time:
                # verify whether experiment is revoking data
                if self.t[index] == None:
                    if self.valid[index]:
                        self.valid[index] = False
                        data['action'] = 'revoke'
                        return data
                else:
                    self.valid[index] = True

                # compute the dts if we have two or more valid inputs
                if sum(self.valid) >= 2:
                    DeltaTMatrix = [[0 for j in range(sum(self.valid))] for i in range(sum(self.valid))]
                    for i in range(sum(self.valid)):
                        for j in range(i+1, sum(self.valid)):
                            DeltaTMatrix[i][j] = np.subtract(self.t[i], self.t[j])

                            if 'dts' not in data:
                                data['dts'] = {(self.dets_names[i], self.dets_names[j]): {'dt': tuple(lib.normalize_time_difference(DeltaTMatrix[i][j])),\
                                                                't1': self.dets_nu_times[i], 't2': self.dets_nu_times[j]}}
                            else:
                                data['dts'].update({(self.dets_names[i], self.dets_names[j]): {'dt': tuple(lib.normalize_time_difference(DeltaTMatrix[i][j])), \
                                                                     't1': self.dets_nu_times[i], 't2': self.dets_nu_times[j]}})

                   # data['dt_uncertainties'] = {"Diff_t0s": max(self.uncertainties)}
                    self.h[index] = data['history']
                    data['history'].combine(list(filter(None, self.h)))

                   # data['history'].combine((self.h[0], self.h[1]))
                   # in fact, this should even work if we return True,
                   # since the payload has been updated in place.
                    logging.warning(data)
                    return data

                # not enough inputs
                return False
            # no update
            return False

        def revoke(self, data):
            index = self.last_watch_index()
            revoke = self.valid[index]
            if revoke:
                self.valid[index] = False
            return revoke

        def reset(self, data):
            reset = False
            if sum(self.valid) >= 1:
                reset = True
            for i in range(len(self.valid)):
                self.valid[i] = False
            return reset

        def report(self, data):
            return True
