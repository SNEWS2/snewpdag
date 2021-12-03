"""
DtsCalculator: compute neutrino time dts between each detector sending an alert.

Input payload:
    data[neutrino_time] = observed burst time for a detector (s,ns). For mc trials use
    the DetectorTime.py plugin to generate this.

Output payload:
    dts: a dictionary of time differences. Keys are of form (det1, det2). The values are themselves dictionaries with
    the following keys:
    dt: time tuple (s,ns) of t1-t2
    t1: neutrino time tuple (s,ns) of det1
    t2: neutrino time tuple (s,ns) of det2
"""

import logging
import numpy as np
from snewpdag.dag import Node, lib

class DtsCalculator(Node):
        def __init__(self, **kwargs):
            self.valid = [False] * 10  # flags indicating valid data from sources
            self.t = [None] * 10  # neutrino time for each detector
            self.h = [0.0] * 10  # histories from each source
            self.dets_names = [None] * 10
            self.dets_nu_times = [0.0] * 10
           # self.uncertainties = [0.0] * 10  # time uncertainties for each source
           # if kwargs.pop('detector_location_file'):
           #     self.db = DetectorDB(kwargs.pop('detector_location_file'))
            super().__init__(**kwargs)

        def alert(self, data):
           # verify whether there are enough input nodes to do a calculation:
            index = self.last_watch_index()
            if index < 0:
                source = self.last_source
                logging.error("[{}] Unrecognized source {}".format(self.name, source))
                return False

           # extract neutrino time for each detector:
            burst_time = self.t[index]
            self.t[index] = data.get('neutrino_time')
            for det_name, nu_time in data['gen']['neutrino_times'].items():
                if nu_time == self.t[index]:
                    #det = self.db.get(det_name)
                    #det_uncertainty = det.sigma
                    #self.uncertainties[index] = det_uncertainty
                    self.dets_names[index] = det_name
                    self.dets_nu_times[index] = nu_time

           # verify whether an experiment is revoking its data:
            if self.t[index] != burst_time:
                if self.t[index] == None:
                    if self.valid[index]:
                        self.valid[index] = False
                        data['action'] = 'revoke'
                        return data
                else:
                    self.valid[index] = True
                self.h[index] = data['history']
               # compute the dts if we have two or more valid inputs
                if sum(self.valid) >= 2:
                   # store dts in a 2d list:
                    DeltaTsMatrix = [[0 for j in range(sum(self.valid))] for i in range(sum(self.valid))]
                    for i in range(sum(self.valid)):
                        for j in range(i+1, sum(self.valid)):
                            DeltaTsMatrix[i][j] = np.subtract(self.t[i], self.t[j])
                           # add to the payload:
                            if 'dts' not in data:
                                data['dts'] = {(self.dets_names[i], self.dets_names[j]): {'dt': tuple(lib.normalize_time_difference(DeltaTsMatrix[i][j])),\
                                                                't1': self.dets_nu_times[i], 't2': self.dets_nu_times[j]}}
                            else:
                                data['dts'].update({(self.dets_names[i], self.dets_names[j]): {'dt': tuple(lib.normalize_time_difference(DeltaTsMatrix[i][j])), \
                                                                     't1': self.dets_nu_times[i], 't2': self.dets_nu_times[j]}})

                   # data['dt_uncertainties'] = {"Diff_t0s": max(self.uncertainties)}

                    logging.warning(self.h[0])
                    logging.warning(self.h[1])
                    logging.warning(self.h[2])
                    data['history'].combine(list(filter(None, self.h)))
                    logging.warning(data)
                    logging.warning(data['history'])


                   # data['history'].combine((self.h[0], self.h[1]))
                   # in fact, this should even work if we return True,
                   # since the payload has been updated in place.
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