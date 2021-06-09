'''
Unit tests for Validator plugin
'''
from snewpdag.values.History import History
import unittest
import numpy as np
from snewpdag.dag import Node
from snewpdag.plugins import Validator

class TestValidator(unittest.TestCase):
    
    def test_plugin0(self):
        h1 = Validator(search_key = 'action', key_type = str, name = 'val0')
        data = [
            {'action': 'alert'},
            {'dt': 1.0},
        ]
        print('Test1')
        self.assertEqual(h1.check_key(data[0]), True)
        self.assertEqual(h1.check_key(data[1]), False)
        self.assertEqual(h1.check_type(data[0]['action']), True)

    def test_plugin1(self):
        # I don't know what the type 'history' belongs to, so this test should fail
        h1 = Validator(search_key = 'dt', key_type = float, name = 'val0')
        data = [
            {'action': 'alert'},
            {'dt': 1.0},
        ]
        print('Test2')
        self.assertEqual(h1.check_key(data[0]), False)
        self.assertEqual(h1.check_key(data[1]), True)
        self.assertEqual(h1.check_type(data[1]['dt']), True)
    
    def test_plugin2(self):
        h1 = History()
        h1.append('Input1')
        h2 = Validator(key_type = History, name = 'val0')
        data = [
            {'history': h1},
        ]
        print('Test3')
        self.assertEqual(h2.check_type(data[0]['history']), True)

    def test_plugin3(self):
        h1 = Validator(key_type = float, name = 'val0')
        data = [
            {'dt': [0.0, 1.0, 2.1, 'bug0', 'bug1', 4.0, 'bug2']},
        ]
        print('Test4')
        self.assertEqual(h1.check_listtype(data[0]['dt']), [0.0, 1.0, 2.1, 4.0])
    
    def test_plugin4(self):
        h1 = Validator(key_type = str, name = 'val0')
        data = [
            {'dt': [0.0, 1.0, 2.1, 'bug', 4.0, 'bug2']},
        ]
        print('Test5')
        self.assertEqual(h1.check_listtype(data[0]['dt']), ['bug', 'bug2'])

    def test_plugin5(self):
        h1 = Validator(order = 'ascending', name = 'val0')
        h2 = Validator(order = 'descending', name = 'val0')
        data = [
            {'dt': [0.0, 1.0, 5.3, 3.2, 0.5]},
            {'dt': [0.0, 1.0, 5.3, 3.2, 0.5]},
        ]
        print('Test6')
        self.assertEqual(h1.check_sorted(data[0]['dt']), [0.0, 0.5, 1.0, 3.2, 5.3])
        self.assertEqual(h2.check_sorted(data[1]['dt']), [5.3, 3.2, 1.0, 0.5, 0.0])

    def test_plugin6(self):
        h1 = Validator(order = 'ascending', name = 'val0')
        h2 = Validator(order = 'descending', name = 'val1')
        h3 = Validator(name = 'val2')
        data = [
            {'dt': [0.0, 0.5, 1.0, 3.2, 5.3]}, # we want this to be in ascending order
            {'dt': [5.3, 3.2, 1.0, 0.5, 0.0]}, # we want this to be in descending order
            {'dt': [0.0, 1.0, 5.3, 3.2, 0.5]}, # we want this to pass unmodified
        ]
        print('Test7')
        self.assertEqual(h1.check_sorted(data[0]['dt']), [0.0, 0.5, 1.0, 3.2, 5.3])
        self.assertEqual(h2.check_sorted(data[1]['dt']), [5.3, 3.2, 1.0, 0.5, 0.0])
        self.assertEqual(h3.check_sorted(data[2]['dt']), [0.0, 1.0, 5.3, 3.2, 0.5])