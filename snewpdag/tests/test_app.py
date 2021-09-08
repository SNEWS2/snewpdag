"""
Unit tests for app methods for configuration and injection.
"""
import unittest
from snewpdag.dag.app import configure, inject

class TestApp(unittest.TestCase):

  def test_configure(self):
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
    nodes = configure(spec)

    self.assertEqual(len(nodes), 4)
    self.assertIn('Input1', nodes)
    self.assertIn('Input2', nodes)
    self.assertIn('Diff1', nodes)
    self.assertIn('Diff3', nodes)

    self.assertEqual(nodes['Input1'].observers,
                     [ nodes['Diff1'], nodes['Diff3'] ])
    self.assertEqual(nodes['Input2'].observers,
                     [ nodes['Diff1'], nodes['Diff3'] ])
    self.assertEqual(nodes['Diff1'].watch_list,
                     [ nodes['Input1'], nodes['Input2'] ])
    self.assertEqual(nodes['Diff3'].watch_list,
                     [ nodes['Input1'], nodes['Input2'] ])
    self.assertEqual(nodes['Diff1'].observers, [])
    self.assertEqual(nodes['Diff3'].observers, [])
    self.assertEqual(nodes['Diff1'].nth, 1)
    self.assertEqual(nodes['Diff3'].nth, 3)

  def test_inject(self):
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

    data = [
      { 'name': 'Input1', 'action': 'alert',
        'times': [ -0.1, 0.1, 0.2, 0.5 ] },
      { 'name': 'Input2', 'action': 'alert',
        'times': [ -0.5, 0.3, 0.6, 1.0 ] },
      ]

    nodes = {}
    nodes[0] = configure(spec)
    inject(nodes, data, spec)
    self.assertEqual(nodes[0]['Diff1'].last_data['action'], 'alert')
    self.assertAlmostEqual(nodes[0]['Diff1'].last_data['dt'], 0.4)
    self.assertEqual(nodes[0]['Diff3'].last_data['action'], 'alert')
    self.assertAlmostEqual(nodes[0]['Diff3'].last_data['dt'], -0.4)
    self.assertEqual(nodes[0]['Diff1'].last_data['history'].emit(),
                     ( (('Input1', ), ('Input2', )), 'Diff1' ) )

    data = [
      { 'name': 'Input2', 'action': 'revoke' }
      ]
    inject(nodes, data, spec)
    self.assertTrue(nodes[0]['Diff1'].valid[0])
    self.assertAlmostEqual(nodes[0]['Diff1'].t[0], -0.1)
    self.assertFalse(nodes[0]['Diff1'].valid[1])
    self.assertEqual(nodes[0]['Diff1'].last_data['action'], 'revoke')
    self.assertTrue(nodes[0]['Diff3'].valid[0])
    self.assertAlmostEqual(nodes[0]['Diff3'].t[0], 0.2)
    self.assertFalse(nodes[0]['Diff3'].valid[1])
    self.assertEqual(nodes[0]['Diff3'].last_data['action'], 'revoke')

    data = [
      { 'name': 'Input1', 'action': 'alert',
        'times': [ 0.0, -0.2, 0.4, 0.1 ] },
      ]
    inject(nodes, data, spec)
    self.assertTrue(nodes[0]['Diff1'].valid[0])
    self.assertAlmostEqual(nodes[0]['Diff1'].t[0], -0.2)
    self.assertFalse(nodes[0]['Diff1'].valid[1])
    self.assertTrue(nodes[0]['Diff3'].valid[0])
    self.assertAlmostEqual(nodes[0]['Diff3'].t[0], 0.1)
    self.assertFalse(nodes[0]['Diff3'].valid[1])
    self.assertEqual(nodes[0]['Diff1'].last_data['action'], 'revoke')
    self.assertEqual(nodes[0]['Diff3'].last_data['action'], 'revoke')

    data = [
      { 'name': 'Input2', 'action': 'alert',
        'times': [ -0.6, 0.3, 1.0, 0.8 ] },
      ]
    inject(nodes, data, spec)
    self.assertEqual(nodes[0]['Diff1'].last_data['action'], 'alert')
    self.assertAlmostEqual(nodes[0]['Diff1'].last_data['dt'], 0.4)
    self.assertEqual(nodes[0]['Diff3'].last_data['action'], 'alert')
    self.assertAlmostEqual(nodes[0]['Diff3'].last_data['dt'], -0.7)

  def test_cyclic_error(self):
    spec = [
      { 'class': 'TimeSeriesInput', 'name': 'Input1' },
      { 'class': 'TimeSeriesInput', 'name': 'Input2' },
      { 'class': 'NthTimeDiff',
        'name': 'Diff1',
        'kwargs': { 'nth': 1 },
        'observe': [ 'Input1', 'Diff1' ] }, # should be an error
      { 'class': 'NthTimeDiff',
        'name': 'Diff3',
        'kwargs': { 'nth': 3 },
        'observe': [ 'Input1', 'Input2' ] },
      ]
    with self.assertLogs() as cm:
      nodes = configure(spec)
    self.assertEqual(cm.output, [
        'ERROR:root:Diff1 observing itself' ])

