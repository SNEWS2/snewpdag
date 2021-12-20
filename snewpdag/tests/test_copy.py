"""
Unit tests for Copy plugin
"""
import unittest

from snewpdag.plugins import Copy

class TestCopy(unittest.TestCase):

  def test_copy_single(self):
    h = Copy([ ['gen/t', 'neutrino_time'] ], name='copy0')
    data = { 'action': 'alert', 'gen' : { 't': 0.5 } }
    ret = h.alert(data)
    self.assertEqual(data['neutrino_time'], 0.5)

    h = Copy([ ['source', 'dest'] ], name='copy1')
    data = { 'action': 'alert', 'source' : 1.0 }
    ret = h.alert(data)
    self.assertEqual(data['dest'], 1.0)

    h = Copy([ ['source', 'dest/value'] ], name='copy2')
    data = { 'action': 'alert', 'source' : 1.0 }
    ret = h.alert(data)
    self.assertEqual(data['dest']['value'], 1.0)

  def test_copy_multiple(self):
    h = Copy([ ['gen/t', 'neutrino_time'], ['gen/x', 'dest/x' ] ],
             name='copy0')
    data = { 'action': 'alert', 'gen' : { 't': 0.5, 'x': 0.25 } }
    ret = h.alert(data)
    self.assertEqual(data['neutrino_time'], 0.5)
    self.assertEqual(data['dest']['x'], 0.25)

