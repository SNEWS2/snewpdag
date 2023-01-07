"""
LogLProb - take a log-likelihood map and turn it into probability map

arguments:
  prefactor: multiple by this before take exp, def -0.5 (for chi2-like input)
  in_field: field name of log-likelihood values
  out_field: field name of probability values
"""
import logging
import numpy as np

from snewpdag.dag import Node

class LogLProb(Node):
  def __init__(self, in_field, out_field, prefactor=-0.5, **kwargs):
    self.in_field = in_field
    self.out_field = out_field
    self.prefactor = prefactor
    super().__init__(**kwargs)

  def alert(self, data):
    if self.in_field in data:
      m = np.array(data[self.in_field])
      #base = np.min(m)
      #v = np.exp((m - base) * self.prefactor)
      v = np.exp(m * self.prefactor)
      sv = np.sum(v)
      logging.info('Sum of probability map is {}'.format(sv))
      data[self.out_field] = v / sv
      return data
    else:
      return False

