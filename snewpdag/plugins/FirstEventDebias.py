"""
FirstEventDebias - assign burst time to first event time - estimated bias
  First version:  histogram in 0.1ms bins, use self to estimate bias.

  Later:
  1. get first event time.
     a. if signal-only time series, this is just the first event
     b. if signal-only histogram, left edge of first non-zero bin
     c. if time series with background, make a histogram and then (d)
     d. if histogram with background, find where deviation is significant,
        and then work back to first bin with signal > 0 after bg subtraction.
  2. calculate bias correction.

Arguments:
  in_field:  input field for a new lightcurve (values.TimeSeries or Hist1D)
  in_ref_field:  input field for reference lightcurve
                 (may be the same as in_field)
  in_truth_field:  input field for true time
  out_field:  output field for corrected burst time
  out_delta_field:  output field for corrected burst time - true time
  ref_template:  True if only use input data for norm, and ref for data.
                 if False (default), use both timeseries to calculate bias.
  lead_time:  lead time in data to determine background level (sec, default 0).
              set to 0 to use no-background assumption.
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field, store_field
from snewpdag.values import TimeSeries, Hist1D

class FirstEventDebias(Node):
  def __init__(self, in_field, in_truth_field,
               out_field, out_delta_field, **kwargs):
    self.in_field = in_field
    #self.in_ref_field = in_ref_field
    self.in_truth_field = in_truth_field
    self.out_field = out_field
    self.out_delta_field = out_delta_field
    #self.ref_template = kwargs.pop('ref_template', False)
    #self.lead_time = kwargs.pop('lead_time', 0.0)
    super().__init__(**kwargs)

  def alert(self, data):
    ts, valid = fetch_field(data, self.in_field)
    if not valid:
      return False

    # determine background level
    stop = ts.start + 5.0
    h, edges = ts.histogram(50000, stop=stop)
    bg_rate = np.sum(h[:10000]) / 10000 # background events / 0.1ms
    hs = h - bg_rate
    logging.debug('{}: h = {}'.format(self.name, h[:10]))

    # first event:  find peak, work back to bin before sub-bg level
    ifirst = np.argmax(hs)
    logging.debug('{}: argmax = {}, hs = {}, h = {}, bg_rate = {}, t = {}'.format(self.name, ifirst, hs[ifirst], h[ifirst], bg_rate, edges[ifirst]))
    ilast = ifirst
    while hs[ifirst] > 0.0:
      ifirst = ifirst - 1
    ifirst = ifirst + 1 # point to a bin above 0
    t0 = edges[ifirst]
    while ilast < len(hs):
      if hs[ilast] <= 0.0:
        break
      ilast = ilast + 1
    logging.debug('{}: ifirst = {}, ilast = {}'.format(self.name, ifirst, ilast))

    # calculate bias correction based on background-subtracted histogram
    #n = np.maximum(hs[ifirst:ilast], 0.0)
    n = hs[ifirst:ilast] # all should be positive
    t = edges[ifirst:ilast]
    sn = np.cumsum(n)
    ex = np.exp(-sn)
    num = n[0] * t[0] + np.sum(n[1:] * t[1:] * ex[:-1])
    denom = n[0] + np.sum(n[1:] * ex[:-1])
    corr = num / denom
    t1 = t0 - corr

    logging.debug('{}: t0 = {}, corr = {}, after = {}'.format(self.name, t0, corr, t1))

    store_field(data, self.out_field, t1)
    t0, valid = fetch_field(data, self.in_truth_field)
    if valid:
      dt = t1 - t0
      store_field(data, self.out_delta_field, dt)
    return True

