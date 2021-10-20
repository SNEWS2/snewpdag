"""
DeltatCalculator: compute the time difference between the observed t0s
                    from the data[neutrino_time] field of two detectors.

Output:
    Time difference between the respective t0s, (s,ns)
"""

import logging
import numpy as np
from snewpdag.dag import Node, lib


class DeltatCalculator(Node):
        def __init__(self, **kwargs):
            self.valid = [False, False]  # flags indicating valid data from sources
            self.t = [0.0, 0.0]  # observed first nu event time for each detector
            self.h = [(), ()]  # histories from each source
            super().__init__(**kwargs)


        def alert(self, data):
            index = self.last_watch_index()
            if index < 0:
                source = self.last_source
                logging.error("[{}] Unrecognized source {}".format(self.name, source))
                return False
            if index >= 2:
                source = self.last_source
                logging.error("[{}] Excess source {} detected".format(self.name, source))
                return False

            newrevoke = False
            self.t[index] = data['neutrino_time']
            if self.t[index] == None:
                if self.valid[index]:
                    self.valid[index] = False
                    newrevoke = True
            else:
                self.valid[index] = True
            self.h[index] = data['history']  # a History object

            # check if there's a new revocation
            # (since we only expect to observe 2 nodes,
            # there's no way to update the time difference)
            if newrevoke:
                return True

            # do the calculation if we have two valid inputs
            if self.valid == [True, True]:
                #compute time difference in sec and ns:
                Deltat= np.subtract(self.t[0], self.t[1])
                data['observed_dt'] = tuple(lib.normalize_time_difference(Deltat))
                print(data['observed_dt'])
                data['history'].combine(self.h)
                print(data)
                # data['history'] = ( self.h[0], self.h[1] )
                # in fact, this should even work if we return True,
                # since the payload has been updated in place.
                return data

            # no update
            return False

        def revoke(self, data):
            index = self.last_watch_index()
            newrevoke = self.valid[index]
            self.valid[index] = False
            return newrevoke

        def reset(self, data):
            newrevoke = self.valid[0] or self.valid[1]
            self.valid[0] = False
            self.valid[1] = False
            return newrevoke

        def report(self, data):
            return True
