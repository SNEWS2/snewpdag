"""
Unit tests for input classes.
"""
import unittest
import logging
from snewpdag.dag import Node
from snewpdag.plugins import TimeSeriesInput

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
        'ERROR:root:[Input1] Expected action field not found' ])
    self.assertEqual(n2.last_data, {})

    data['action'] = 'alert'
    with self.assertLogs() as cm:
      n1.update(data)
    self.assertEqual(cm.output, [
        'ERROR:root:[Input1] Expected times field not found' ])
    self.assertEqual(n2.last_data, {})

