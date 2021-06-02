'''
Unit tests for Action Filter plugin
'''
import unittest
import numpy as np
from snewpdag.dag import Node
from snewpdag.plugins import ActionFilter

class TestActionFilter(unittest.TestCase):
    
    def test_plugin0(self):
        h = ActionFilter(name='acc0')
        data = [
            { 'action': 'alert', 'newaction': 'report' }, # only for MC
        ] # 'onalert' = 'report'
        self.assertEqual(h.change_action(data[0]), None)
        self.assertEqual(h.alert(data[0]), False)
        self.assertEqual(h.revoke(data[0]), False)
        self.assertEqual(h.reset(data[0]), False)
        self.assertEqual(h.report(data[0]), True)
    
    def test_plugin1(self):
        h = ActionFilter(name='acc0')
        data = [
            { 'action': 'alert' },
        ] 
        self.assertEqual(h.change_action(data), None)
        self.assertEqual(h.alert(data), False)
        self.assertEqual(h.revoke(data), False)
        self.assertEqual(h.reset(data), False)
        self.assertEqual(h.report(data), False)    
    