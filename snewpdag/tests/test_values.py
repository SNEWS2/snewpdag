"""
Unit tests for value objects
"""
import unittest
import numpy as np
from snewpdag.values import Hist1D, TimeHist, TimeSeries
from snewpdag.dag.lib import ns_per_second

class TestHist1D(unittest.TestCase):

  def test_construct(self):
    h = Hist1D(100, 1.0, 3.0)
    self.assertEqual(h.nbins, 100)
    self.assertEqual(h.xlow, 1.0)
    self.assertEqual(h.xhigh, 3.0)
    self.assertEqual(h.xwidth, 2.0)

  def test_timehist(self):
    h = TimeHist((3,5), 5, 10, [5, 4, 3, 2, 1, 10, 9, 8, 7, 6, 18])
    self.assertEqual(h.nbins(), 10)
    t3 = h.bin_start(6)
    self.assertEqual(t3[0], 6)
    self.assertEqual(t3[1], 5)
    self.assertEqual(h.bins[3], 2)
    offsets = np.array([0.6, 12.0, 3.2, -0.8]) * ns_per_second
    h.add_offsets(offsets)
    self.assertEqual(h.bins[0], 5)
    self.assertEqual(h.bins[1], 5)
    self.assertEqual(h.bins[2], 3)
    self.assertEqual(h.bins[3], 2)
    self.assertEqual(h.bins[4], 1)
    self.assertEqual(h.bins[5], 10)
    self.assertEqual(h.bins[6], 10)
    self.assertEqual(h.bins[7], 8)
    self.assertEqual(h.bins[8], 7)
    self.assertEqual(h.bins[9], 6)
    h.add_times([(3,7), (8,3), (2,1)])
    self.assertEqual(h.bins[0], 6)
    self.assertEqual(h.bins[1], 5)
    self.assertEqual(h.bins[2], 3)
    self.assertEqual(h.bins[3], 2)
    self.assertEqual(h.bins[4], 1)
    self.assertEqual(h.bins[5], 10)
    self.assertEqual(h.bins[6], 10)
    self.assertEqual(h.bins[7], 8)
    self.assertEqual(h.bins[8], 7)
    self.assertEqual(h.bins[9], 7)

  def test_timeseries(self):
    s = TimeSeries((3,5))
    s.add_offsets([1000, 200, 400])
    self.assertEqual(s.times[0], 200)
    self.assertEqual(s.times[1], 400)
    self.assertEqual(s.times[2], 1000)
    s.add_times([(5,7), (8,3), (2,1)])
    self.assertEqual(s.times[0], - ns_per_second - 4)
    self.assertEqual(s.times[1], 200)
    self.assertEqual(s.times[2], 400)
    self.assertEqual(s.times[3], 1000)
    self.assertEqual(s.times[4], 2*ns_per_second + 2)
    self.assertEqual(s.times[5], 5*ns_per_second - 2)
    t = s.event(1)
    self.assertEqual(t[0], 3)
    self.assertEqual(t[1], 205)
    t = s.event([1,2])
    self.assertEqual(t[0][0], 3)
    self.assertEqual(t[0][1], 205)
    self.assertEqual(t[1][0], 3)
    self.assertEqual(t[1][1], 405)

