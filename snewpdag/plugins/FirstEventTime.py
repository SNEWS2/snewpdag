"""
FirstEventTime - assign burst time to first event time.
  Also compare with true time if available.

Arguments:
  in_field:  input field for a new time series (type values.TimeSeries)
  in_truth_field:  input field for true time
  out_field:  output field for burst time
  out_delta_field:  output field for burst - true time
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field, store_field

class FirstEventTime(Node):
  def __init__(self, in_field, in_truth_field,
               out_field, out_delta_field, **kwargs):
    self.in_field = in_field
    self.in_truth_field = in_truth_field
    self.out_field = out_field
    self.out_delta_field = out_delta_field
    super().__init__(**kwargs)

  def alert(self, data):
    ts, valid = fetch_field(data, self.in_field) # TimeSeries
    if not valid:
      return False
    t1 = np.min(ts.times)
    logging.debug('t1 = {}'.format(t1))
    store_field(data, self.out_field, t1)
    t0, valid = fetch_field(data, self.in_truth_field)
    if valid:
      logging.debug('t0 = {}'.format(t0))
      dt = t1 - t0
      store_field(data, self.out_delta_field, dt)
    return True

