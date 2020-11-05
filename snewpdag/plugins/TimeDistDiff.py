"""
TimeDistDiff:  plugin which gives time differences between time distributions

Input JSON: (choose either cl or chi2)

If cl or chi2 are lists rather than numpy arrays, they're converted.
JSON input fields:
    't':  low edges of time bins (array of floats)
    'n':  number of events in corresponding time bins (array of floats)

Output JSON:
    dictionary of input pairs with time difference (TODO - pyhonise the format)

Author: V. Kulikovskiy (kulikovs@ge.infn.it)
"""
import logging
import numpy as np

from snewpdag.dag import Node

class TimeDistDiff(Node):
  def __init__(self, **kwargs):
    self.map = {}
    super().__init__(**kwargs)

  def update(self, data):
    action = data['action']
    source = data['history'][-1]
 
    if action == 'alert':
      if 't' in data and 'n' in data:
        self.map[source] = data
        self.map[source]['valid'] = True
      else:
        logging.error('[{}] Expected t and n arrays in time distribution'.format(self.name))
        return
    elif action == 'revoke':
      if source in self.map:
        self.map[source]['valid'] = False
      else:
        logging.error('[{}] Revocation received for unknown source {}'.format(self.name, source))
        return
    else:
      logging.error("[{}] Unrecognized action {}".format(self.name, action))
      return


    # start constructing output data.
    ndata = {}

    # first, see if there is any valid data.  if so, alert. otherwise revoke.
    hlist = []
    for k in self.map:
      if self.map[k]['valid']:
        hlist.append(self.map[k]['history'])
    ndata['action'] = 'revoke' if len(hlist) == 0 else 'alert'
    ndata['history'] = tuple(hlist)

    # do the calculation

    # notify
    self.notify(ndata)
