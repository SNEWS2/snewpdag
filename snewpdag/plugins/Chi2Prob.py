"""
Chi2Prob - take a chi2 map and turn it into probability map

arguments:
  in_field: field name of chi2 values
  out_field: field name of probability values

Note that chi2 is calculated at the center of each pixel (in DiffPointing),
so the calculation here starts by calculating the probability density at
each pixel center.  We take this central pdf value as proportional to
the average probability over the pixel.  Since all healpix pixels have
equal area, we sum all these pdf values and then divide by the sum.
The result should be a probability map normalized to unit area,
within the central-value-as-average approximation.

Confidence levels calculated with the resulting skymap won't be quite the
same as those calculated with Chi2CL, given the approximations in both.
"""
import logging
import numpy as np
from scipy.stats import chi2

from snewpdag.dag import Node

class Chi2Prob(Node):
  def __init__(self, in_field, out_field, **kwargs):
    self.in_field = in_field
    self.out_field = out_field
    super().__init__(**kwargs)

  def alert(self, data):
    if self.in_field in data:
      m = np.array(data[self.in_field])
      base = np.min(m)
      v = m - base
      c = chi2.pdf(v, df=2)
      sc = np.sum(c)
      logging.info('Sum of probability map is {}'.format(sc))
      data[self.out_field] = c / sc
      return data
    else:
      return False

