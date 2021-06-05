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

  def alert(self, data):
    source = data['history'][-1]
    if 'cl' in data and 'chi2' in data:
      logging.error('[{}] Both CL and chi2 present in map'.format(self.name))
      return False
    if 'cl' in data or 'chi2' in data:
      self.map[source] = data.copy()
      self.map[source]['valid'] = True
      return self.reevaluate(data)
    else:
      logging.error('[{}] Expected either CL or chi2 in map'.format(self.name))
      return False

  def revoke(self, data):
    source = data['history'][-1]
    if source in self.map:
      self.map[source]['valid'] = False
      return self.reevaluate(data)
    else:
      logging.error('[{}] Revocation received for unknown source {}'.format(
                    self.name, source))
      return False

  def reset(self, data):
    newrevoke = False
    for k in self.map:
      if self.map[k]['valid']:
        newrevoke = True
        self.map[k]['valid'] = False
    return newrevoke

  def reevaluate(self, data):
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
      data['chi2'] = m
      data['ndof'] = df

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
      data['cl'] = m

    # notify
    hlist = []
    for k in self.map:
      if self.map[k]['valid']:
        hlist.append(self.map[k]['history'])
    data['action'] = 'revoke' if len(hlist) == 0 else 'alert'
    data['history'] = tuple(hlist)
    return data

