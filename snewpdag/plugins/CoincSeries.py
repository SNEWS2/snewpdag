"""
CoincSeries - make a new series out of coincidences.
  A coincidence is an event followed closely by another.
  Therefore 3 events close in time will count as two coincidences,
  with the first two times providing the coincidence times.

Arguments:
  in_series_field
  out_series_field
  pair_time:  coincidence window in s
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field, store_field
from snewpdag.values import TimeSeries

class CoincSeries(Node):
  def __init__(self, in_series_field, out_series_field, pair_time, **kwargs):
    self.in_series_field = in_series_field
    self.out_series_field = out_series_field
    self.pair_time = pair_time
    super().__init__(**kwargs)

  def alert(self, data):
    ts, valid = fetch_field(data, self.in_series_field)
    if not valid:
      return False
    tsort = np.sort(ts.times)
    tsort0 = tsort[:-1]
    dt = tsort[1:] - tsort0
    tc = tsort0[dt < self.pair_time]
    ss = TimeSeries(ts.start, ts.stop)
    ss.add(tc)
    store_field(data, self.out_series_field, ss)
    logging.debug('{}: input length = {}, output length = {}'.format(self.name, len(tsort), len(tc)))
    return True

