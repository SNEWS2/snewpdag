"""
LagPull - calculate pull for lag

Arguments:
  in_obs_field: input field containing observed value
  in_err_field: input field containing error on observed value
  in_true_field: input field containing true value
  in_base_field: optional input field to subtract from true value
  out_field: output field to store (obs - (true - base)) / err
  on: list of 'alert', 'report', 'revoke', 'reset'
"""
import logging
from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field

class LagPull(Node):
  def __init__(self, out_field, in_obs_field, in_err_field, in_true_field,
               in_base_field = None, on = ['alert'], **kwargs):
    self.out_field = out_field
    self.in_obs_field = in_obs_field
    self.in_err_field = in_err_field
    self.in_true_field = in_true_field
    self.in_base_field = in_base_field
    self.on = on
    super().__init__(**kwargs)

  def calc(self, data):
    obs, exists = fetch_field(data, self.in_obs_field)
    if not exists:
      return False
    err, exists = fetch_field(data, self.in_err_field)
    if not exists:
      return False
    if err == 0.0:
      return False
    truth, exists = fetch_field(data, self.in_true_field)
    if not exists:
      return False
    if self.in_base_field == None:
      base = 0.0
    else:
      base, exists = fetch_field(data, self.in_base_field)
      if not exists:
        return False
    if isinstance(err, (list, tuple)):
      dx = obs - (truth - base)
      sigm = abs(err[0])
      sigp = abs(err[1])
      data[self.out_field] = dx / (sigm if dx < 0 else sigp)
    else:
      data[self.out_field] = (obs - (truth - base)) / err
    return data

  def alert(self, data):
    return self.calc(data) if 'alert' in self.on else True

  def revoke(self, data):
    return self.calc(data) if 'revoke' in self.on else True

  def reset(self, data):
    return self.calc(data) if 'reset' in self.on else True

  def report(self, data):
    return self.calc(data) if 'report' in self.on else True

