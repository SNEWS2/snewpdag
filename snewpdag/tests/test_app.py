"""
Unit tests for app methods for configuration and injection.
"""
import unittest
from snewpdag.dag.app import configure, inject

class TestApp(unittest.TestCase):

  def setUp(self):
    spec = [
      { 'class': 'TimeSeriesInput', 'name': 'Input1' },
      { 'class': 'TimeSeriesInput', 'name': 'Input2' },
      { 'class': 'NthTimeDiff',
        'name': 'Diff1',
        'kwargs': { 'nth': 1 },
        'observe': [ 'Input1', 'Input2' ] },
      { 'class': 'NthTimeDiff',
        'name': 'Diff3',
        'kwargs': { 'nth': 3 },
        'observe': [ 'Input1', 'Input2' ] },
      ]
    self.nodes = configure(spec)

  def test_configure(self):
    self.assertEqual(len(self.nodes), 4)
    self.assertIn('Input1', self.nodes)
    self.assertIn('Input2', self.nodes)
    self.assertIn('Diff1', self.nodes)
    self.assertIn('Diff3', self.nodes)

    self.assertEqual(self.nodes['Input1'].observers,
                     [ self.nodes['Diff1'], self.nodes['Diff3'] ])
    self.assertEqual(self.nodes['Input2'].observers,
                     [ self.nodes['Diff1'], self.nodes['Diff3'] ])
    self.assertEqual(self.nodes['Diff1'].watch_list,
                     [ self.nodes['Input1'], self.nodes['Input2'] ])
    self.assertEqual(self.nodes['Diff3'].watch_list,
                     [ self.nodes['Input1'], self.nodes['Input2'] ])
    self.assertEqual(self.nodes['Diff1'].observers, [])
    self.assertEqual(self.nodes['Diff3'].observers, [])
    self.assertEqual(self.nodes['Diff1'].nth, 1)
    self.assertEqual(self.nodes['Diff3'].nth, 3)

  def test_inject(self):
    data = [
      { 'name': 'Input1', 'action': 'alert',
        'times': [ -0.1, 0.1, 0.2, 0.5 ] },
      { 'name': 'Input2', 'action': 'alert',
        'times': [ -0.5, 0.3, 0.6, 1.0 ] },
      ]
    inject(self.nodes, data)
    self.assertEqual(self.nodes['Diff1'].last_data,
        { 'action': 'alert', 'dt': 0.4,
          'history': ( ('Input1', ), ('Input2', ), 'Diff1' ) })
    self.assertEqual(self.nodes['Diff1'].last_data['action'], 'alert')
    self.assertAlmostEqual(self.nodes['Diff1'].last_data['dt'], 0.4)
    self.assertEqual(self.nodes['Diff3'].last_data['action'], 'alert')
    self.assertAlmostEqual(self.nodes['Diff3'].last_data['dt'], -0.4)

    data = [
      { 'name': 'Input2', 'action': 'revoke' }
      ]
    inject(self.nodes, data)
    self.assertTrue(self.nodes['Diff1'].valid[0])
    self.assertAlmostEqual(self.nodes['Diff1'].t[0], -0.1)
    self.assertFalse(self.nodes['Diff1'].valid[1])
    self.assertEqual(self.nodes['Diff1'].last_data['action'], 'revoke')
    self.assertTrue(self.nodes['Diff3'].valid[0])
    self.assertAlmostEqual(self.nodes['Diff3'].t[0], 0.2)
    self.assertFalse(self.nodes['Diff3'].valid[1])
    self.assertEqual(self.nodes['Diff3'].last_data['action'], 'revoke')

    data = [
      { 'name': 'Input1', 'action': 'alert',
        'times': [ 0.0, -0.2, 0.4, 0.1 ] },
      ]
    inject(self.nodes, data)
    self.assertTrue(self.nodes['Diff1'].valid[0])
    self.assertAlmostEqual(self.nodes['Diff1'].t[0], -0.2)
    self.assertFalse(self.nodes['Diff1'].valid[1])
    self.assertTrue(self.nodes['Diff3'].valid[0])
    self.assertAlmostEqual(self.nodes['Diff3'].t[0], 0.1)
    self.assertFalse(self.nodes['Diff3'].valid[1])
    self.assertEqual(self.nodes['Diff1'].last_data['action'], 'revoke')
    self.assertEqual(self.nodes['Diff3'].last_data['action'], 'revoke')

    data = [
      { 'name': 'Input2', 'action': 'alert',
        'times': [ -0.6, 0.3, 1.0, 0.8 ] },
      ]
    inject(self.nodes, data)
    self.assertEqual(self.nodes['Diff1'].last_data['action'], 'alert')
    self.assertAlmostEqual(self.nodes['Diff1'].last_data['dt'], 0.4)
    self.assertEqual(self.nodes['Diff3'].last_data['action'], 'alert')
    self.assertAlmostEqual(self.nodes['Diff3'].last_data['dt'], -0.7)

