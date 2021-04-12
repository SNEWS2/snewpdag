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

  def update(self, data):
    action = data['action']
    source = data['history'][-1]

    # figure out which source updated
    index = self.watch_index(source)
    if index < 0:
      logging.error("[{}] Unrecognized source {}".format(self.name, source))
      return
    if index >= 2:
      logging.error("[{}] Excess source {} detected".format(self.name, source))
      return

    # update the relevant data.
    # Only issue a downstream revocation if the source revocation
    # is new, i.e., the data was valid before.
    newrevoke = False
    if action == 'alert':
      self.t[index] = self.get_nth(data['times'])
      if self.t[index] == None:
        if self.valid[index]:
          self.valid[index] = False
          newrevoke = True
      else:
        self.valid[index] = True
      self.h[index] = data['history']
    elif action == 'revoke':
      newrevoke = self.valid[index]
      self.valid[index] = False
    elif action == 'reset':
      newrevoke = self.valid[0] or self.valid[1]
      self.valid[0] = False
      self.valid[1] = False
    elif action == 'report':
      self.notify(action, None, data)
      return
    else:
      logging.error("[{}] Unrecognized action {}".format(self.name, action))
      return

    # check of there's a new revocation
    if newrevoke:
      self.notify(action, None, data)
      return

    # do the calculation if we have two valid inputs.
    if self.valid == [ True, True ]:
      ndata = data.copy()
      ndata['t0'] = self.t[0]
      ndata['t1'] = self.t[1]
      ndata['dt'] = self.t[0] - self.t[1]
      if 'times' in ndata:
        del ndata['times']
      self.notify('alert', ( self.h[0], self.h[1] ), ndata)

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

