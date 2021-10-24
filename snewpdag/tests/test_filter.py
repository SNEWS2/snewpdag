"""
Unit tests for Filter plugins
"""
import unittest

from snewpdag.plugins import FilterValue

class TestFilter(unittest.TestCase):

  def test_filter_value(self):
    fv = FilterValue('test', 10.0, name='fv0')
    data = { 'action': 'alert', 'test': 10.0 }
    ret = fv.alert(data)
    self.assertEqual(ret, True)
    data = { 'action': 'alert', 'test': 11.0 }
    ret = fv.alert(data)
    self.assertEqual(ret, False)
    data = { 'action': 'alert' }
    ret = fv.alert(data)
    self.assertEqual(ret, False)
    # test pass-throughs
    data = { 'action': 'reset' }
    ret = fv.reset(data)
    self.assertEqual(ret, True)
    data = { 'action': 'revoke' }
    ret = fv.revoke(data)
    self.assertEqual(ret, True)
    data = { 'action': 'report' }
    ret = fv.report(data)
    self.assertEqual(ret, True)

  def test_filter_other_actions(self):
    fv = FilterValue('test', 10.0, name='fv0', on_alert=False,
                     on_reset=True, on_revoke=True, on_report=True)
    data = { 'action': 'action' }
    ret = fv.alert(data)
    self.assertEqual(ret, True)
    data = { 'action': 'reset', 'test': 10.0 }
    ret = fv.reset(data)
    self.assertEqual(ret, True)
    data = { 'action': 'reset', 'test': 11.0 }
    ret = fv.reset(data)
    self.assertEqual(ret, False)
    data = { 'action': 'reset' }
    ret = fv.reset(data)
    self.assertEqual(ret, False)
    data = { 'action': 'revoke', 'test': 10.0 }
    ret = fv.revoke(data)
    self.assertEqual(ret, True)
    data = { 'action': 'revoke', 'test': 11.0 }
    ret = fv.revoke(data)
    self.assertEqual(ret, False)
    data = { 'action': 'revoke' }
    ret = fv.revoke(data)
    self.assertEqual(ret, False)
    data = { 'action': 'report', 'test': 10.0 }
    ret = fv.revoke(data)
    self.assertEqual(ret, True)
    data = { 'action': 'report', 'test': 11.0 }
    ret = fv.revoke(data)
    self.assertEqual(ret, False)
    data = { 'action': 'report' }
    ret = fv.revoke(data)
    self.assertEqual(ret, False)

