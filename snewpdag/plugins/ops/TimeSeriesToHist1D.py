"""
TimeSeriesToHist1D - use a TimeSeries to fill a Hist1D.

Arguments:
  in_field:  input field name
  out_field:  output field name
  nbins:  number of bins
  start:  float to indicate start time
  stop:  float to indicate stop time
"""
import logging
import numpy as np
from astropy.time import Time
from snewpdag.dag import Node
from snewpdag.values import Hist1D, TimeSeries

class TimeSeriesToHist1D(Node):
  def __init__(self, in_field, out_field, nbins, start, stop, **kwargs):
    self.in_field = in_field
    self.out_field = out_field
    self.nbins = nbins
    self.start = start
    if isinstance(self.start, str):
      self.start = Time(self.start).to_value('unix', 'long')
    self.stop = stop
    if isinstance(self.stop, str):
      self.stop = Time(self.stop).to_value('unix', 'long')
    super().__init__(**kwargs)

  def alert(self, data):
    if self.in_field in data:
      ts = data[self.in_field]
      if isinstance(ts, TimeSeries):
        th = Hist1D(self.nbins, self.start, self.stop)
        th.fill(ts.times)
        data[self.out_field] = th
        return data
    return False

