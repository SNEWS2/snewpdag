"""
Unit tests for Histogram plugin
"""
import unittest
import numpy as np
from snewpdag.dag import Node
from snewpdag.plugins import Histogram1D

class TestHistogram1D(unittest.TestCase):

  def test_plugin0(self):
    h = Histogram1D(10, -0.1, 1.9, 'dt', name='hist0')
    data = [
             { 'action': 'alert', 'dt': 0.1 },
             { 'action': 'alert', 'dt': 0.3 },
             { 'action': 'alert', 'dt': 0.8 },
             { 'action': 'alert', 'dt': 2.1 },
             { 'action': 'alert', 'dt': -1.0 },
           ]
    for d in data:
      h.update(d)

    h.update({ 'action': 'report' })
    hh = h.last_data['histogram']
    self.assertEqual(h.last_data['action'], 'report')
    self.assertEqual(h.last_data['history'], ('hist0',))
    self.assertEqual(hh['name'], 'hist0')
    self.assertEqual(hh['nbins'], 10)
    self.assertAlmostEqual(hh['xlow'], -0.1)
    self.assertAlmostEqual(hh['xhigh'], 1.9)
    self.assertEqual(hh['in_field'], 'dt')
    self.assertIsNone(hh['in_index'])
    self.assertEqual(hh['underflow'], 1)
    self.assertEqual(hh['overflow'], 1)
    self.assertAlmostEqual(hh['sum'], 2.3)
    self.assertAlmostEqual(hh['sum2'], 6.15)
    self.assertEqual(hh['count'], 5)
    self.assertEqual(hh['bins'].tolist(), [ 0, 1, 1, 0, 1, 0, 0, 0, 0, 0 ])
    # if there were actual floats here, we could use
    #np.assert_allclose(hh['bins'], [ 0, 1, 1, 0, 1, 0, 0, 0, 0, 0 ])
    # and then use a @staticmethod decorator to avoid pylint errors

  def test_plugin1d(self):
    h = Histogram1D(10, -0.1, 1.9, 'dt', index=2, name='hist1')
    data = [
             { 'action': 'alert', 'dt': [0.0, 0.0, 0.1, 0.0] },
             { 'action': 'alert', 'dt': [0.0, 0.0, 0.3, 0.0] },
             { 'action': 'alert', 'dt': [0.0, 0.0, 0.8, 0.0] },
             { 'action': 'alert', 'dt': [0.0, 0.0, 2.1, 0.0] },
             { 'action': 'alert', 'dt': [0.0, 0.0, -1.0, 0.0] },
           ]
    for d in data:
      h.update(d)

    h.update({ 'action': 'report' })
    hh = h.last_data['histogram']
    self.assertEqual(h.last_data['action'], 'report')
    self.assertEqual(h.last_data['history'], ('hist1',))
    self.assertEqual(hh['name'], 'hist1')
    self.assertEqual(hh['nbins'], 10)
    self.assertAlmostEqual(hh['xlow'], -0.1)
    self.assertAlmostEqual(hh['xhigh'], 1.9)
    self.assertEqual(hh['in_field'], 'dt')
    self.assertEqual(hh['in_index'], 2)
    self.assertEqual(hh['underflow'], 1)
    self.assertEqual(hh['overflow'], 1)
    self.assertAlmostEqual(hh['sum'], 2.3)
    self.assertAlmostEqual(hh['sum2'], 6.15)
    self.assertEqual(hh['count'], 5)
    self.assertEqual(hh['bins'].tolist(), [ 0, 1, 1, 0, 1, 0, 0, 0, 0, 0 ])

  def test_plugin2d(self):
    h = Histogram1D(10, -0.1, 1.9, 'dt', index=(1, 2), name='hist2')
    d0 = np.zeros((3,3))
    d1 = np.zeros((3,3))
    d2 = np.zeros((3,3))
    d3 = np.zeros((3,3))
    d4 = np.zeros((3,3))
    d0[1,2] = 0.1
    d1[1,2] = 0.3
    d2[1,2] = 0.8
    d3[1,2] = 2.1
    d4[1,2] = -1.0
    data = [
             { 'action': 'alert', 'dt': d0 },
             { 'action': 'alert', 'dt': d1 },
             { 'action': 'alert', 'dt': d2 },
             { 'action': 'alert', 'dt': d3 },
             { 'action': 'alert', 'dt': d4 },
           ]
    for d in data:
      h.update(d)

    h.update({ 'action': 'report' })
    hh = h.last_data['histogram']
    self.assertEqual(h.last_data['action'], 'report')
    self.assertEqual(h.last_data['history'], ('hist2',))
    self.assertEqual(hh['name'], 'hist2')
    self.assertEqual(hh['nbins'], 10)
    self.assertAlmostEqual(hh['xlow'], -0.1)
    self.assertAlmostEqual(hh['xhigh'], 1.9)
    self.assertEqual(hh['in_field'], 'dt')
    self.assertEqual(hh['in_index'], (1,2))
    self.assertEqual(hh['underflow'], 1)
    self.assertEqual(hh['overflow'], 1)
    self.assertAlmostEqual(hh['sum'], 2.3)
    self.assertAlmostEqual(hh['sum2'], 6.15)
    self.assertEqual(hh['count'], 5)
    self.assertEqual(hh['bins'].tolist(), [ 0, 1, 1, 0, 1, 0, 0, 0, 0, 0 ])

  def test_summary(self):
    h = Histogram1D(10, -0.1, 1.9, 'dt', name='hist0')
    data = [
             { 'action': 'alert', 'dt': 0.1 },
             { 'action': 'alert', 'dt': 0.3 },
             { 'action': 'alert', 'dt': 0.8 },
             { 'action': 'alert', 'dt': 2.1 },
             { 'action': 'alert', 'dt': -1.0 },
           ]
    for d in data:
      h.update(d)

    hh = h.summary()
    self.assertEqual(hh['name'], 'hist0')
    self.assertEqual(hh['nbins'], 10)
    self.assertAlmostEqual(hh['xlow'], -0.1)
    self.assertAlmostEqual(hh['xhigh'], 1.9)
    self.assertEqual(hh['in_field'], 'dt')
    self.assertIsNone(hh['in_index'])
    self.assertEqual(hh['underflow'], 1)
    self.assertEqual(hh['overflow'], 1)
    self.assertAlmostEqual(hh['sum'], 2.3)
    self.assertAlmostEqual(hh['sum2'], 6.15)
    self.assertEqual(hh['count'], 5)
    self.assertEqual(hh['bins'].tolist(), [ 0, 1, 1, 0, 1, 0, 0, 0, 0, 0 ])

    self.assertAlmostEqual(h.mean(), 2.3 / 5.0)
    self.assertAlmostEqual(h.variance(), 6.15/5.0 - 2.3*2.3/(5.0*5.0))

  def test_reset(self):
    h = Histogram1D(10, -0.1, 1.9, 'dt', name='hist0')
    data = [
             { 'action': 'alert', 'dt': 0.1 },
             { 'action': 'alert', 'dt': 0.3 },
             { 'action': 'alert', 'dt': 0.8 },
             { 'action': 'alert', 'dt': 2.1 },
             { 'action': 'alert', 'dt': -1.0 },
           ]
    for d in data:
      h.update(d)

    hh = h.summary()
    self.assertEqual(hh['count'], 5)
    h.reset()
    hh = h.summary()
    self.assertEqual(hh['count'], 0)
    self.assertEqual(hh['sum'], 0.0)
    self.assertEqual(hh['sum2'], 0.0)
    self.assertEqual(hh['underflow'], 0.0)
    self.assertEqual(hh['overflow'], 0.0)
    self.assertEqual(hh['bins'].tolist(), [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ])

