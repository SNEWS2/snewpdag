"""
Author: M. Colomer (marta.colomer@ulb.be)

"""
import logging
import numpy as np

from snewpdag.dag import Node

class True_VS_Fit(Node):
  def __init__(self, in_field, **kwargs):
    self.map = {}

    self.field = in_field

    v = kwargs.pop('in_index', None)
    self.index = tuple(v) if isinstance(v, list) else v
    v = kwargs.pop('in_index2', None)
    self.index2 = tuple(v) if isinstance(v, list) else v

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
    dt_JUNO = -9999
    dt_IC = -9999
    # do the calculation
    for n,i in enumerate(self.map):
       if(i=='JUNO'):
         dt_JUNO = self.map[i]['t_true']
         print('Hey there', self.map[i]['t_true'])
       if(i=='IceCube'):
         dt_IC = self.map[i]['t_true']
         print('Hey there', self.map[i]['t_true'])
       if(i=='Diff1'):
         dt_fit = self.map[i][self.field][self.index][self.index2]
         print('Hey there', self.map[i][self.field][self.index][self.index2])
       print('hihi', n,i)
    print('Heeeeelo', dt_fit, dt_IC, dt_JUNO)
    data['dt_true'] = dt_fit - (dt_IC - dt_JUNO)

    hlist = []
    for k in self.map:
      if self.map[k]['valid']:
        hlist.append(self.map[k]['history'])
    if len(hlist) > 1:
      action_verb = 'alert'
      data['history'].combine(hlist)
      self.notify(action_verb, data)
    #print('I notify', data, result)
    #exit()
