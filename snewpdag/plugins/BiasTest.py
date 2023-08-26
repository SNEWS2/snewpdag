"""
BiasTest - test bias estimate

Arguments:
  in_series1_field
  in_series2_field
  out_delta_field:  delta based on first events of series
  out_exp_field:  <delta> estimate based on series
  out_dev_field:  delta - <delta>
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field, store_field

class BiasTest(Node):
  def __init__(self, in_series1_field, in_series2_field,
               out_delta_field, out_exp_field, out_dev_field, **kwargs):
    self.in_series1_field = in_series1_field
    self.in_series2_field = in_series2_field
    self.out_delta_field = out_delta_field
    self.out_exp_field = out_exp_field
    self.out_dev_field = out_dev_field
    super().__init__(**kwargs)

  def alert(self, data):
    ts1, valid = fetch_field(data, self.in_series1_field) # TimeSeries
    if not valid:
      return False
    ts2, valid = fetch_field(data, self.in_series2_field) # TimeSeries
    if not valid:
      return False

    # difference between first times
    tf1 = np.min(ts1.times)
    tf2 = np.min(ts2.times)
    dtf = tf1 - tf2
    store_field(data, self.out_delta_field, dtf)

    # expected value of delta
    # note that aside from alpha, this only depends on first series
    alpha = len(ts2.times) / len(ts1.times)
    s1 = np.sort(ts1.times)
    k1 = range(len(s1))
    ik1 = np.arange(len(s1)) + 1.0
    e1 = np.exp(-ik1)
    e2 = np.exp(-alpha*ik1)
    dte = np.sum(e1*s1)/np.sum(e1) - np.sum(e2*s1)/np.sum(e2)
    store_field(data, self.out_exp_field, dte)

    # deviation
    dev = dtf - dte
    store_field(data, self.out_dev_field, dev)

    logging.debug('{}: dtf = {}, dte = {}, dev = {}'.format(self.name, dtf, dte, dev))
    return True

