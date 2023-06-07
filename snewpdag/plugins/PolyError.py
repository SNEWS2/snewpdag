"""
PolyError - calculate error parameters from smoothed polynomial

Arguments:
  in_field: input field containing a numpy Polynomial
  out_field: output field containing xmax, xerr, xdiff
  in_stdl_field: optional field name for scaling error
  error_scale: optional parameter for scaling error
  x_range: +- range in x for polynomial domain
  on: list of 'action', 'report', 'revoke', 'reset'
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field

class PolyError(Node):
  def __init__(self, in_field, out_field, x_range=0.04, **kwargs):
    self.in_field = in_field
    self.out_field = out_field
    self.x_range = x_range
    self.in_stdl_field = kwargs.pop('in_stdl_field', '')
    self.error_scale = kwargs.pop('error_scale', 0.0)
    self.on = kwargs.pop('on', ['alert'])
    super().__init__(**kwargs)

  def operate(self, data):
    p, exists = fetch_field(data, self.in_field) # p should be Polynomial
    if not exists:
      logging.error('{}: input field {} does not exist'.format(self.name, self.in_field))
      return False
    stdl = 0.0 # stddev of logL around smoothed polynomial
    if self.in_stdl_field != '':
      stdl, exists = fetch_field(data, self.in_stdl_field)
      if not exists:
        stdl = 0.0
    d1 = p.deriv()
    d2 = d1.deriv()
    logging.debug('{}: poly = {} {}'.format(self.name, p, p.mapparms()))
    logging.debug('{}:   d1 = {} {}'.format(self.name, d1, d1.mapparms()))
    logging.debug('{}:   d2 = {} {}'.format(self.name, d2, d2.mapparms()))
    logging.debug('{}: stdl = {}'.format(self.name, stdl))
    xext = d1.roots()
    vext = xext[ np.abs(xext) < self.x_range ]
    v2 = d2(vext)
    if len(v2) == 0:
      logging.error('{}: no extrema returned in range'.format(self.name))
      return False
    i = np.argmin(v2) # should be most negative in valid range
    if v2[i] >= 0.0:
      logging.error('{}: invalid 2nd derivative {}'.format(self.name, v2))
      return False
    xmax = np.real_if_close(vext[i]) - 0.0 # subtract 0 to convert array to num
    # use second derivative for symmetric error
    xerr = np.sqrt(- (1.0 + self.error_scale * stdl) / np.real_if_close(v2[i]))
    # use polynomial limits instead
    pmod = (p - p(xmax) + 0.5 + self.error_scale * stdl)
    xr = pmod.roots()
    xa = np.real_if_close(xr)
    xd = xa[np.isreal(xa)] - xmax # deviations from xmax
    # select closest roots on either side of xmax
    if len(xd) > 0:
      logging.debug('  d1 roots = {}'.format(xext))
      logging.debug('  d2 at d1 roots = {}'.format(v2))
      logging.debug('  xmax = {}'.format(xmax))
      logging.debug('pmod = {}'.format(pmod))
      logging.debug('xr = {}'.format(xr))
      logging.debug('xa = {}'.format(xa))
      logging.debug('xd = {}'.format(xd))
      xps = xd[xd > 0]
      xms = xd[xd < 0]
      if len(xps) == 0 or len(xms) == 0:
        logging.error('{}: one-sided roots, xmax={}, roots-xmax={}, poly={}'.format(self.name, xmax, xd, pmod))
      xp = np.min(xps) if len(xps) > 0 else xerr
      xm = np.max(xms) if len(xms) > 0 else xerr
      logging.debug('(xm, xp) = ({}, {})'.format(xm,xp))
    else:
      # weird if no real roots, but recover by using symmetric errors for now
      logging.error('{}: no real roots of polynomial {}'.format(self.name, pmod))
      xp = xerr
      xm = xerr
    data[self.out_field] = { 'xmax': xmax, \
                             'xerr': xerr, \
                             'xerr2': xerr*xerr, \
                             'xdiff': (-xm, xp), }
    return data

  def alert(self, data):
    return self.operate(data) if 'alert' in self.on else True

  def report(self, data):
    return self.operate(data) if 'report' in self.on else True

