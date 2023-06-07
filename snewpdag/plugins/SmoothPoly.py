"""
SmoothPoly - fit (x,y) data with a polynomial

This was for error evaluation, so calculates some things relevant for that.
Could be moved to another module which works on the returned polynomial.
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field

class SmoothPoly(Node):
  def __init__(self, in_x_field, in_y_field, out_field, degree=4, **kwargs):
    self.in_x_field = in_x_field
    self.in_y_field = in_y_field
    self.out_field = out_field
    self.degree = degree
    self.on = kwargs.pop('on', ['alert'])
    super().__init__(**kwargs)

  def operate(self, data):
    #logging.info('{}: x field = {}, y field = {}'.format(self.name, self.in_x_field, self.in_y_field))
    x, exists = fetch_field(data, self.in_x_field)
    if not exists:
      logging.error('{}: x field {} does not exist'.format(self.name, self.in_x_field))
      logging.error('data keys = {}'.format(data.keys()))
      logging.error('history = {}'.format(data['history']))
      return False
    y, exists = fetch_field(data, self.in_y_field)
    if not exists:
      logging.error('{}: y field {} does not exist'.format(self.name, self.in_y_field))
      return False
    r = (np.min(x), np.max(x))
    p = np.polynomial.polynomial.Polynomial.fit(x, y, self.degree, domain=r, window=r)
    xp = np.array(x)
    yp = p(xp)
    dyp = y - yp
    std = np.std(dyp)
    logging.debug('{}: polynomial = {} {}'.format(self.name, p, p.mapparms()))
    data[self.out_field] = { 'polynomial': p, 'y': yp, 'std': std }
    return data

  def alert(self, data):
    return self.operate(data) if 'alert' in self.on else True

  def report(self, data):
    return self.operate(data) if 'report' in self.on else True

