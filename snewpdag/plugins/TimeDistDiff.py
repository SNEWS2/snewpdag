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

    # first, see if there are at least two valid data sets.  if so, alert. otherwise revoke.
    hlist = []
    for k in self.map:
      if self.map[k]['valid']:
        hlist.append(self.map[k]['history'])
    ndata['action'] = 'revoke' if len(hlist) <= 1 else 'alert'
    ndata['history'] = tuple(hlist)

    ndata['tdelay'] = {}
    # do the calculation
    for i in self.map:
        for j in self.map:
            if i < j:
                #here the main time difference calculation comes
                ndata['tdelay'][(i,j)] = gettdelay(self.map[i]['t'],self.map[i]['n'],self.map[j]['t'],self.map[j]['n'])

    # notify
    self.notify(ndata)

def gettdelay(t1,n1,t2,n2):
    #dummy output for now
    return (len(t1), len(n1), len(t2), len(n2))
