"""
Unit tests for value objects
"""
import unittest
from snewpdag.values import Hist1D

class TestHist1D(unittest.TestCase):

  def test_construct(self):
    h = Hist1D(100, 1.0, 3.0)
    self.assertEqual(h.nbins, 100)
    self.assertEqual(h.xlow, 1.0)
    self.assertEqual(h.xhigh, 3.0)
    self.assertEqual(h.xwidth, 2.0)

