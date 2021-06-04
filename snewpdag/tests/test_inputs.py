"""
Unit tests for input classes.
"""
import unittest
import logging
from snewpdag.dag import Node
from snewpdag.plugins import TimeSeriesInput, TimeDistFileInput

class TestInputs(unittest.TestCase):

  def test_time_series(self):
    n1 = TimeSeriesInput(name='Input1')
    n2 = Node('Node2')
    n1.attach(n2)
    data = { 'action': 'alert', 'times': [ -0.2, 0.1, 0.125 ] };
    n1.update(data)
    self.assertEqual(n2.last_data,
                     { 'action': 'alert',
                       'times': [ -0.2, 0.1, 0.125 ],
                       'history': ( 'Input1', 'Node2' ) } )

  def test_time_series_invalid_input(self):
    n1 = TimeSeriesInput(name='Input1')
    n2 = Node('Node2')
    n1.attach(n2)
    data = { 'time': [ -0.2, 0.1, 0.125 ] };
    with self.assertLogs() as cm:
      n1.update(data)
    self.assertEqual(cm.output, [
        'ERROR:root:[Input1] Action not specified' ])
    self.assertEqual(n2.last_data, {})

    data['action'] = 'alert'
    with self.assertLogs() as cm:
      n1.update(data)
    self.assertEqual(cm.output, [
        'ERROR:root:[Input1] Expected times field not found' ])
    self.assertEqual(n2.last_data, {})

  def test_timedistfile(self):
    n1 = TimeDistFileInput(name='Input1')
    n2 = Node('Node2')
    n1.attach(n2)
    data = { 'filename': 'null.txt', 'filetype': 'tn' }
    with self.assertLogs() as cm:
      n1.update(data)
    self.assertEqual(cm.output, [
        'ERROR:root:[Input1] Action not specified' ])
    self.assertEqual(n2.last_data, {})

    data = { 'action': 'alert', 'filetype': 'tn' }
    with self.assertLogs() as cm:
      n1.update(data)
    self.assertEqual(cm.output, [
        'ERROR:root:[Input1] Missing filename' ])
    self.assertEqual(n2.last_data, {})

    data = { 'action': 'alert', 'filename': 'null.txt', 'filetype': 'hist' }
    with self.assertLogs() as cm:
      n1.update(data)
    self.assertEqual(cm.output, [
        'ERROR:root:[Input1] Unrecognized file type hist' ])
    self.assertEqual(n2.last_data, {})

    data = { 'action': 'alert',
             'filename': 'snewpdag/data/fluxparametrisation_22.5kT_0Hz_0.0msT0_1msbin.txt',
             'filetype': 'tn' }
    n1.update(data)
    self.assertEqual(len(n2.last_data['t_low']), 9999)
    self.assertEqual(len(n2.last_data['t_bins']), 9999)
    self.assertEqual(n2.last_data['t_low'][2125], 0.125)
    self.assertEqual(n2.last_data['t_bins'][2125], 7)
    self.assertEqual(n2.last_data['t_low'][2500], 0.5)
    self.assertEqual(n2.last_data['t_bins'][2500], 1)

