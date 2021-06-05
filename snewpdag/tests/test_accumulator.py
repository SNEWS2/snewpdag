"""
Unit tests for Accumulator plugin
"""
import unittest
import numpy as np
from snewpdag.dag import Node
from snewpdag.plugins import Accumulator

class TestAccumulator(unittest.TestCase):

  def test_plugin0(self):
    h = Accumulator('Time diffs', 'dt', name='acc0')
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
    self.assertEqual(h.last_data['history'], ('acc0',))
    self.assertEqual(hh['name'], 'acc0')
    self.assertEqual(hh['title'], 'Time diffs')
    self.assertEqual(hh['in_field'], 'dt')
    self.assertIsNone(hh['in_index'])
    dd = hh['series']
    self.assertEqual(len(dd), 5)
    self.assertAlmostEqual(dd[0], 0.1)
    self.assertAlmostEqual(dd[1], 0.3)
    self.assertAlmostEqual(dd[2], 0.8)
    self.assertAlmostEqual(dd[3], 2.1)
    self.assertAlmostEqual(dd[4], -1.0)

  def test_plugin1(self):
    h = Accumulator('Time diffs', 'dt', index=2, name='acc0')
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
    self.assertEqual(h.last_data['history'], ('acc0',))
    self.assertEqual(hh['name'], 'acc0')
    self.assertEqual(hh['title'], 'Time diffs')
    self.assertEqual(hh['in_field'], 'dt')
    self.assertEqual(hh['in_index'], 2)
    dd = hh['series']
    self.assertEqual(len(dd), 5)
    self.assertAlmostEqual(dd[0], 0.1)
    self.assertAlmostEqual(dd[1], 0.3)
    self.assertAlmostEqual(dd[2], 0.8)
    self.assertAlmostEqual(dd[3], 2.1)
    self.assertAlmostEqual(dd[4], -1.0)

  def test_plugin2(self):
    h = Accumulator('Time diffs', 'dt', index=(1, 2), name='acc0')
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
    self.assertEqual(h.last_data['history'], ('acc0',))
    self.assertEqual(hh['name'], 'acc0')
    self.assertEqual(hh['title'], 'Time diffs')
    self.assertEqual(hh['in_field'], 'dt')
    self.assertEqual(hh['in_index'], (1, 2))
    dd = hh['series']
    self.assertEqual(len(dd), 5)
    self.assertAlmostEqual(dd[0], 0.1)
    self.assertAlmostEqual(dd[1], 0.3)
    self.assertAlmostEqual(dd[2], 0.8)
    self.assertAlmostEqual(dd[3], 2.1)
    self.assertAlmostEqual(dd[4], -1.0)

  def test_summary(self):
    h = Accumulator('Time diffs', 'dt', name='acc0')
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
    dd = hh['series']
    self.assertEqual(len(dd), 5)
    self.assertAlmostEqual(dd[0], 0.1)
    self.assertAlmostEqual(dd[1], 0.3)
    self.assertAlmostEqual(dd[2], 0.8)
    self.assertAlmostEqual(dd[3], 2.1)
    self.assertAlmostEqual(dd[4], -1.0)

  def test_reset(self):
    h = Accumulator('Time diffs', 'dt', name='acc0')
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
    self.assertEqual(len(hh['series']), 5)
    self.assertAlmostEqual(hh['series'][1], 0.3)
    h.reset()
    hh = h.summary()
    self.assertEqual(hh['series'], [])

