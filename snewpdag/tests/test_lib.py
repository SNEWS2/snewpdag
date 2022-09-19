"""
Unit tests for dag library methods
"""
import unittest
from snewpdag.dag.lib import *

class TestLib(unittest.TestCase):

  def test_convert(self):
    t = t2ns(3.5)
    self.assertEqual(t, 3500000000)
    t = t2ns([4.5, 2.25])
    self.assertEqual(t[0], 4500000000)
    self.assertEqual(t[1], 2250000000)
    t = t2ns(-3.5)
    self.assertEqual(t, -3500000000)
    t = t2ns([-4.5, -0.25])
    self.assertEqual(t[0], -4500000000)
    self.assertEqual(t[1], -250000000)
    t = t2ns(3.5 * u.ms)
    self.assertEqual(t, 3500000)
    t = t2ns(3.5, unit=u.us)
    self.assertEqual(t, 3500)
    t = t2ns(48, unit=u.ns)
    self.assertEqual(t, 48)

  def test_fetch_field(self):
    data1 = { 'f10': 10, 'f11': 11 }
    data2 = { 'f20': data1, 'f21': 21 }
    data3 = { 'f30': 30, 'f31': data2 }
    data4 = { 'f40': 40, 'f41': data3 }
    data5 = { 'f50': 50, 'f51': [ 510, 511, 512 ], 'f52': [ data4, data1 ] }
    v, flag = fetch_field(data4, 'f40')
    self.assertTrue(flag)
    self.assertEqual(v, 40)
    v, flag = fetch_field(data4, ('f40',))
    self.assertTrue(flag)
    self.assertEqual(v, 40)
    v, flag = fetch_field(data4, ('f41','f30',))
    self.assertTrue(flag)
    self.assertEqual(v, 30)
    v, flag = fetch_field(data4, ['f41','f31','f21'])
    self.assertTrue(flag)
    self.assertEqual(v, 21)
    v, flag = fetch_field(data4, ['f41','f31','f20','f11'])
    self.assertTrue(flag)
    self.assertEqual(v, 11)
    v, flag = fetch_field(data4, ('f41','f31','f20',))
    self.assertTrue(flag)
    self.assertEqual(v, data1)
    v, flag = fetch_field(data4, ('f42',))
    self.assertFalse(flag)
    self.assertEqual(v, None)
    v, flag = fetch_field(data4, ('f41','f32'))
    self.assertFalse(flag)
    self.assertEqual(v, None)
    v, flag = fetch_field(data4, ('f41','f30','f20',))
    self.assertFalse(flag)
    self.assertEqual(v, None)
    v, flag = fetch_field(data5, ('f51',1))
    self.assertTrue(flag)
    self.assertEqual(v, 511)
    v, flag = fetch_field(data5, ('f52',1,'f11'))
    self.assertTrue(flag)
    self.assertEqual(v, 11)

