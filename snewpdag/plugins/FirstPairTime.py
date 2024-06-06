"""
FirstPairTime - assign burst time to first event of a pair within a window.
  Also compare with true time if available.

Arguments:
  max_dt:  maximum time between events in a pair (sec, default 0.015)
  in_field:  input field for a new time series (type values.TimeSeries)
  in_truth_field:  input field for true time
  out_field:  output field for burst time
  out_delta_field:  output field for burst - true time
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field, store_field

class FirstPairTime(Node):
  def __init__(self, in_field, in_truth_field,
               out_field, out_delta_field, **kwargs):
    self.in_field = in_field
    self.in_truth_field = in_truth_field
    self.out_field = out_field
    self.out_delta_field = out_delta_field
    self.max_dt = kwargs.pop('max_dt', 0.015)
    super().__init__(**kwargs)

  def alert(self, data):
    ts, valid = fetch_field(data, self.in_field) # TimeSeries
    if not valid:
      return False
    tsort = np.sort(ts.times)
    dt = tsort[1:] - tsort[:-1]
    for i in range(len(dt)):
      if dt[i] < self.max_dt:
        t1 = tsort[i]
        logging.debug('t1 = {}, i = {}, dt = {}'.format(t1, i, dt[i]))
        store_field(data, self.out_field, t1)
        t0, valid = fetch_field(data, self.in_truth_field)
        if valid:
          offset = t1 - t0
          logging.debug('t0 = {}, offset = {}'.format(t0, offset))
          store_field(data, self.out_delta_field, offset)
        return True
    return False

