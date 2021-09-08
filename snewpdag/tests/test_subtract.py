"""
Unit tests for SubtractOffset plugin
"""
import unittest
import numpy as np
from snewpdag.dag import Node
from snewpdag.plugins import SubtractOffset

class TestSubtractOffset(unittest.TestCase):

  def test_basic(self):
    h = SubtractOffset(2.0, 'times', name='Zero')
    odata = [ 1.0, 5.0, 2.5, 10.0 ]
    data = { 'action': 'alert', 'times': odata }
    h.update(data)
    d = h.last_data['times']
    self.assertEqual(d[0], -1.0)
    self.assertEqual(d[1],  3.0)
    self.assertEqual(d[2],  0.5)
    self.assertEqual(d[3],  8.0)
    self.assertEqual(odata[0], 1.0)
    self.assertEqual(odata[1], 5.0)
    self.assertEqual(odata[2], 2.5)
    self.assertEqual(odata[3], 10.0)

  def test_out_field(self):
    h = SubtractOffset(2.0, 'times', out_field='newtimes', name='Zero')
    odata = [ 1.0, 5.0, 2.5, 10.0 ]
    data = { 'action': 'alert', 'times': odata }
    h.update(data)
    d = h.last_data['newtimes']
    od = h.last_data['times']
    self.assertEqual(d[0], -1.0)
    self.assertEqual(d[1],  3.0)
    self.assertEqual(d[2],  0.5)
    self.assertEqual(d[3],  8.0)
    self.assertEqual(odata[0], 1.0)
    self.assertEqual(odata[1], 5.0)
    self.assertEqual(odata[2], 2.5)
    self.assertEqual(odata[3], 10.0)
    self.assertEqual(od[0], 1.0)
    self.assertEqual(od[1], 5.0)
    self.assertEqual(od[2], 2.5)
    self.assertEqual(od[3], 10.0)

  def test_field_offset(self):
    h = SubtractOffset('t0', 'times', name='Zero')
    odata = [ 1.0, 5.0, 2.5, 10.0 ]
    data = { 'action': 'alert', 'times': odata, 't0': 0.5 }
    h.update(data)
    d = h.last_data['times']
    self.assertEqual(d[0], 0.5)
    self.assertEqual(d[1], 4.5)
    self.assertEqual(d[2], 2.0)
    self.assertEqual(d[3], 9.5)
    self.assertEqual(odata[0], 1.0)
    self.assertEqual(odata[1], 5.0)
    self.assertEqual(odata[2], 2.5)
    self.assertEqual(odata[3], 10.0)

