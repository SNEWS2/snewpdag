"""
Unit tests for value objects
"""
import unittest
import numpy as np
from astropy import units as u
from snewpdag.values import Hist1D, THist, TSeries
from snewpdag.dag.lib import ns_per_second

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

  def test_timehist(self):
    h = THist((3,5), 10, (3,5), (8,5))
    self.assertEqual(h.start, 0)
    self.assertEqual(h.stop, 5*ns_per_second)
    h.bins = np.array([5, 4, 3, 2, 1, 10, 9, 8, 7, 6])
    self.assertEqual(h.nbins, 10)
    t3 = h.bin_start(6)
    self.assertEqual(t3, 6*ns_per_second + 5)
    self.assertEqual(h.bins[3], 2)
    offsets = np.array([0.6, 12.0, 3.2, -0.8])
    h.add_offsets(offsets) # s assumed
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
    h.add_times(np.array([3*ns_per_second+7, \
                          8*ns_per_second+3, \
                          2*ns_per_second+1]) * u.ns)
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
    h.add_times(4.5) # s assumed
    self.assertEqual(h.bins[2], 4)
    h.add_times([1.0, 4.75, 5.5]) # s assumed
    self.assertEqual(h.bins[2], 4)
    self.assertEqual(h.bins[3], 3)
    self.assertEqual(h.bins[4], 2)
    self.assertEqual(h.bins[5], 10)
    self.assertEqual(h.bins[6], 10)
    h.add_offsets(1.25) # s assumed
    self.assertEqual(h.bins[2], 5)
    h.add_offsets([4.25, 8.3, 3.1]) # s assumed
    self.assertEqual(h.bins[6], 11)
    self.assertEqual(h.bins[8], 8)
    h.add_offsets(1250 * u.ms)
    self.assertEqual(h.bins[2], 6)
    h.add_offsets(np.array([4250, 8300, 3100]) * u.ms)
    self.assertEqual(h.bins[6], 12)
    self.assertEqual(h.bins[8], 9)
    h.add_times((4*ns_per_second+4) * u.ns)
    self.assertEqual(h.bins[1], 6)
    h.add_times([4,4]) # s assumed
    self.assertEqual(h.bins[1], 8)
    h.add_times(np.array([4,4])) # s assumed
    self.assertEqual(h.bins[1], 10)

  def test_timeseries(self):
    s = TSeries((3,5))
    s.add_offsets(np.array([1000, 200, 400]) * u.ns)
    s.sort()
    self.assertEqual(s.offsets[0], 200)
    self.assertEqual(s.offsets[1], 400)
    self.assertEqual(s.offsets[2], 1000)
    s.add_times(np.array([5*ns_per_second+7, \
                          8*ns_per_second+3,  \
                          2*ns_per_second+1]) * u.ns)
    s.sort()
    self.assertEqual(s.offsets[0], - ns_per_second - 4)
    self.assertEqual(s.offsets[1], 200)
    self.assertEqual(s.offsets[2], 400)
    self.assertEqual(s.offsets[3], 1000)
    self.assertEqual(s.offsets[4], 2*ns_per_second + 2)
    self.assertEqual(s.offsets[5], 5*ns_per_second - 2)
    t = s.event(1)
    self.assertEqual(t, 3*ns_per_second + 205)
    t = s.event([1,2])
    self.assertEqual(t[0], 3*ns_per_second + 205)
    self.assertEqual(t[1], 3*ns_per_second + 405)
    s.add_offsets(2500 * u.ns)
    s.sort()
    self.assertEqual(s.offsets[4], 2500)
    s.add_offsets(2.5) # s assumed
    s.sort()
    self.assertEqual(s.offsets[6], 2.5 * ns_per_second)
    s.add_offsets(250.0 * u.ms)
    s.sort()
    self.assertEqual(s.offsets[5], 250000000)
    s.add_offsets(np.array([30910, 35801]) * u.ns)
    s.sort()
    self.assertEqual(s.offsets[5], 30910)
    self.assertEqual(s.offsets[6], 35801)
    s.add_offsets([10.5, 12.25]) # s assumed
    s.sort()
    self.assertEqual(s.offsets[11], 10.5 * ns_per_second)
    self.assertEqual(s.offsets[12], 12.25 * ns_per_second)
    s.add_offsets(np.array([15750, 18125]) * u.ms)
    s.sort()
    self.assertEqual(s.offsets[13], 15.75 * ns_per_second)
    self.assertEqual(s.offsets[14], 18.125 * ns_per_second)
    # check that (4,4) vs [4,4] ambiguity resolved in add_times
    s.add_times((4*ns_per_second+4) * u.ns)
    s.sort()
    self.assertEqual(s.offsets[8], ns_per_second - 1)
    s.add_times([4,4]) # array of seconds
    s.sort()
    self.assertEqual(s.offsets[8], ns_per_second - 5)
    self.assertEqual(s.offsets[9], ns_per_second - 5)
    self.assertEqual(s.offsets[10], ns_per_second - 1)
    s.add_times(np.array([5,5])) # s assumed
    s.sort()
    self.assertEqual(s.offsets[11], 2 * ns_per_second - 5)
    self.assertEqual(s.offsets[12], 2 * ns_per_second - 5)

