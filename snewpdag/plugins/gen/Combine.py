"""
Combine - combine generator output

Alert input:
* gen: array of dictionaries.  For each,
  * times: array of floats (event times in seconds).
           Combine will simply concatenate all of them.
  * t_bins: array of floats (bin contents). Combine will add.
  * t_low: float or array of floats (low edges).
  * t_high: float (high edge).

Alert output:
* times
* t_bins
* t_low
* t_high
"""
import sys
import logging
import numpy as np

from snewpdag.dag import Node

class Combine(Node):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

  def alert(self, data):
    if 'gen' not in data:
      logger.warning('{0}: no gen data to combine'.format(self.name))
      return False

    # time series
    tsa = [] # list of times arrays to concatenate
    for d in data['gen']:
      if 'times' in d:
        tsa.append(d['times'])
    if len(tsa) > 0:
      data['times'] = np.concatenate(tsa)
      data['times'].flags.writeable = False

    # histograms - only works if all of them have the same spec
    nodef = True
    for d in data['gen']:
      if 't_true' in d:
        data['t_true'] = d['t_true']
      if 't_bins' in d and 't_low' in d and 't_high' in d:
        if nodef:
          tb = np.array(d['t_bins'])
          tl = d['t_low']
          th = d['t_high']
          tlscalar = np.isscalar(tl)
          nodef = False
        else:
          # test if spec is the same.
          if th == d['t_high'] and len(tb) == len(d['t_bins']) and \
              ((tlscalar and tl == d['t_low']) or \
               (not tscalar and np.allclose(tl, d['t_low']))):
            tb += d['t_bins']
          else:
            logging.warning('{0}: mismatched histogram specs'.format(self.name))
    if not nodef:
      data['t_low'] = tl # assume immutable already
      data['t_high'] = th
      data['t_bins'] = tb
      data['t_bins'].flags.writeable = False
   
    #print(data['t_true'])
    #exit()
    return True

