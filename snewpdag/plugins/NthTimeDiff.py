"""
NthTimeDiff:  plugin which takes two time series
              and returns the time difference between the nth
              events in each series.
Note that nth=1 means taking the first event in time.

Configuration json:
  nth:  which event to choose

Output json:
  alert:
    t0, t1:  times used to calculate dt
    dt:  time differences (t0 - t1)
    delete times field
  revoke, reset, report:  input json unmodified
"""
import logging

from snewpdag.dag import Node

class NthTimeDiff(Node):
  def __init__(self, nth, **kwargs):
    self.nth = nth # input parameter, specifying which event to choose
    self.valid = [ False, False ] # flags indicating valid data from sources
    self.t = [ 0.0, 0.0 ] # nth times for each source
    self.h = [ (), () ] # histories from each source
    super().__init__(**kwargs)
    if self.nth < 1:
      logging.error('[{}] Invalid event index {}, changed to 1'.format(
                    self.name, self.nth))
      self.nth = 1

  def alert(self, data):
    index = self.last_watch_index()
    if index < 0:
      source = data['history'][-1]
      logging.error("[{}] Unrecognized source {}".format(self.name, source))
      return False
    if index >= 2:
      source = data['history'][-1]
      logging.error("[{}] Excess source {} detected".format(self.name, source))
      return False

    newrevoke = False
    self.t[index] = self.get_nth(data['times'])
    if self.t[index] == None:
      if self.valid[index]:
        self.valid[index] = False
        newrevoke = True
    else:
      self.valid[index] = True
    self.h[index] = data['history']

    # check if there's a new revocation
    # (since we only expect to observe 2 nodes,
    # there's no way to update the time difference)
    if newrevoke:
      return True

    # do the calculation if we have two valid inputs
    if self.valid == [ True, True ]:
      data['t0'] = self.t[0]
      data['t1'] = self.t[1]
      data['dt'] = self.t[0] - self.t[1]
      data['history'] = ( self.h[0], self.h[1] )
      # in fact, this should even work if we return True,
      # since the payload has been updated in place.
      return data

    # no update
    return False

  def revoke(self, data):
    newrevoke = self.valid[index]
    self.valid = False
    return newrevoke

  def reset(self, data):
    newrevoke = self.valid[0] or self.valid[1]
    self.valid[0] = False
    self.valid[1] = False
    return newrevoke

  def report(self, data):
    return True

  def get_nth(self, values):
    """
    get nth smallest value in the list of values.
    note that smallest is nth=1
    """
    if len(values) < self.nth:
      return None
    lowest = [ values[i] for i in range(self.nth) ]
    current = max(lowest)
    for i in range(self.nth, len(values)):
      v = values[i]
      if v < current:
        lowest.remove(current)
        lowest.append(v)
        current = max(lowest)
    return current

