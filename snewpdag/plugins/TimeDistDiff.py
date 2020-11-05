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
    super().__init__(**kwargs)

  def update(self, data):
    action = data['action']
    source = data['history'][-1]

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
