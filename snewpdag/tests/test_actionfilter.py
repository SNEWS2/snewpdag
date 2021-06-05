'''
Unit tests for Action Filter plugin
'''
import unittest
import numpy as np
from snewpdag.dag import Node
from snewpdag.plugins import ActionFilter

class TestActionFilter(unittest.TestCase):
    
    def test_plugin0(self):
        h = ActionFilter(on_alert = 'report', on_reset = None, name = 'act0')
        data = [
            { 'action': 'alert' },
            { 'action': 'report' },
        ]
        # self.assertEqual(h.change_action(data[0]), None)
        self.assertEqual(h.alert(data[0])['action'], 'report')
        self.assertEqual(h.reset(data[0]), False)
        self.assertEqual(h.revoke(data[0]), False)
        self.assertEqual(h.report(data[0]), False)

        self.assertEqual(h.alert(data[1])['action'], 'report')
        self.assertEqual(h.reset(data[1]), False)
        self.assertEqual(h.revoke(data[1]), False)
        self.assertEqual(h.report(data[1]), False)

    
    def test_plugin1(self):
        h = ActionFilter(on_report = 'reset', on_alert = None, name = 'act0')
        data = [
            { 'action': 'report' },
        ] 
        self.assertEqual(h.alert(data[0]), False)
        self.assertEqual(h.reset(data[0]), False)
        self.assertEqual(h.revoke(data[0]), False)
        self.assertEqual(h.report(data[0])['action'], 'reset')  
    