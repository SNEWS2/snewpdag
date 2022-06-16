"""
Unit tests for value objects
"""
import unittest
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
    self.assertEqual(s.times[5], 3*ns_per_second - 2)
    self.assertEqual(s.event(1), (3,205))
