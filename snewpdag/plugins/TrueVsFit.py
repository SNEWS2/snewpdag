"""
Code which computes the difference between:
i) True time delay between det1 and det2
ii) Estimated/measured time delay
Provides time uncertainty as ouput

Author: M. Colomer (marta.colomer@ulb.be)

"""
import logging
import numpy as np

from snewpdag.dag import Node

class TrueVsFit(Node):
  def __init__(self, in_field, **kwargs):
    self.map = {}

    self.field = in_field

    super().__init__(**kwargs)

  def update(self, data):
    action = data['action']
    source = data['history'].last()
    #source = data['history'][-1]

    if action == 'alert':
        self.map[source] = data.copy()
        self.map[source]['history'] = data['history'].copy() # keep local copy
        self.map[source]['valid'] = True
    elif action == 'revoke':
      if source in self.map:
        self.map[source]['valid'] = False
      else:
        logging.error('[{}] Revocation received for unknown source {}'.format(self.name, source))
        return
    elif action == 'reset':
      for source in self.map:
        self.map[source]['valid'] = False
      self.notify(action, data)
      return
    elif action == 'report':
      self.notify(action, data)
      return
    else:
      logging.error("[{}] Unrecognized action {}".format(self.name, action))
      return

    # start constructing output data.
    data['dt_true'] = {}
    dt_fit = -9999
    dt_1 = -9999
    dt_2 = -9999
    # do the calculation

    for n,i in enumerate(self.map):
       if(i!='Diff1'):
         if(dt_1==-9999):
           dt_1 = self.map[i]['t_true']
         else:
           dt_2 = self.map[i]['t_true']
       else:
         dt_fit = self.map[i][self.field]
       #print(i, dt_1, dt_2, dt_fit)
    data['dt_true'] = dt_fit - (dt_1 - dt_2)

    hlist = []
    for k in self.map:
      if self.map[k]['valid']:
        hlist.append(self.map[k]['history'])
    if len(hlist) > 1:
      action_verb = 'alert'
      data['history'].combine(hlist)
      self.notify(action_verb, data)
