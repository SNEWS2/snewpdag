"""
Unit tests for value objects
"""
import unittest
import numpy as np
from snewpdag.values import Hist1D, TimeSeries

class TestHist1D(unittest.TestCase):

  def test_construct(self):
    h = Hist1D(100, 1.0, 3.0)
    self.assertEqual(h.nbins, 100)
    self.assertEqual(h.xlow, 1.0)
    self.assertEqual(h.xhigh, 3.0)
    self.assertEqual(h.xwidth, 2.0)

  def test_hist1d(self):
    h = Hist1D(100, 1.0, 3.0)
    h.fill(1.5)
    self.assertEqual(h.bins[25], 1.0)
    h.fill([2.0, 2.5, 3.5, 1.5, -1.0])
    self.assertEqual(h.bins[25], 2.0)
    self.assertEqual(h.bins[50], 1.0)
    self.assertEqual(h.bins[75], 1.0)
    self.assertEqual(h.overflow, 1.0)
    self.assertEqual(h.underflow, 1.0)

  def test_timeseries(self):
    s = TimeSeries() # no limits
    s.add([1000, 200, 400])
    s.sort()
    self.assertEqual(s.times[0], 200)
    self.assertEqual(s.times[1], 400)
    self.assertEqual(s.times[2], 1000)
    s.add(250)
    s.sort()
    self.assertEqual(s.times[0], 200)
    self.assertEqual(s.times[1], 250)
    self.assertEqual(s.times[2], 400)
    self.assertEqual(s.times[3], 1000)

