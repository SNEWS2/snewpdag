"""
CombineMaps:  plugin which combines probabilities in healpix skymaps

Input JSON: (choose either cl or chi2)
  'cl': confidence levels (np.ndarray)
  'chi2': confidence levels in chi2 form (np.ndarray)
  'ndof': number of degrees of freedom, required if using chi2

If cl or chi2 are lists rather than numpy arrays, they're converted.

Output JSON: same fields.

The finest-grained healpix pixellation is chosen.
We use the healpy.ud_grade() function to upgrade.
The map is always assumed to be in nested order.

May also add a function to input.
"""
import logging
import numpy as np
import healpy as hp
from scipy.stats import chi2

from snewpdag.dag import Node

class CombineMaps(Node):
  def __init__(self, force_cl, **kwargs):
    self.force_cl = force_cl # force output in CL
    self.map = {}
    super().__init__(**kwargs)

  def update(self, data):
    action = data['action']
    source = data['history'][-1]

    if action == 'alert':
      if 'cl' in data and 'chi2' in data:
        logging.error('[{}] Both CL and chi2 present in map'.format(self.name))
        return
      if 'cl' in data or 'chi2' in data:
        self.map[source] = data
        self.map[source]['valid'] = True
      else:
        logging.error('[{}] Expected either CL or chi2 in map'.format(self.name))
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

    # if all maps are chi2, then can output chi2
    use_chi2 = not self.force_cl
    if use_chi2:
      for k in self.map:
        if self.map[k]['valid'] and 'cl' in self.map[k]:
          use_chi2 = False
          break

    # find finest binning.
    # for nested ordering, nside values can only be powers of 2,
    # so just take largest value
    npixs = [ len(self.map[k]['chi2']) if 'chi2' in self.map[k]
              else len(self.map[k]['cl'])
              for k in self.map ]
    maxnpix = max(npixs)
    nside = hp.npix2nside(maxnpix)

    # do the calculation
    if use_chi2:
      m = np.zeros(maxnpix)
      df = 0
      for k in self.map:
        v = self.map[k]
        if v['valid']:
          if len(v['chi2']) != len(m):
            ma = hp.ud_grade(np.array(v['chi2']), nside,
                             order_in='NESTED', order_out='NESTED')
          else:
            ma = np.array(v['chi2'])
          m += ma
          df += v['ndof']
      ndata['chi2'] = m
      ndata['ndof'] = df

    else:
      m = np.ones(maxnpix)
      for k in self.map:
        v = self.map[k]
        if v['valid']:
          if 'chi2' in v:
            rv = chi2(v['ndof'])
            mp = rv.cdf(np.array(v['chi2']))
            if len(v['chi2']) != len(m):
              ma = hp.ud_grade(mp, nside,
                               order_in='NESTED', order_out='NESTED')
            else:
              ma = mp
          else:
            if len(v['cl']) != len(m):
              ma = hp.ud_grade(np.array(v['cl']), nside,
                               order_in='NESTED', order_out='NESTED')
            else:
              ma = np.array(v['cl'])
          m *= ma
      ndata['cl'] = m

    # notify
    hlist = []
    for k in self.map:
      if self.map[k]['valid']:
        hlist.append(self.map[k]['history'])
    action_verb = 'revoke' if len(hlist) == 0 else 'alert'
    self.notify(action_verb, tuple(hlist), ndata)

