"""
Basic tests of the Node class by itself.
"""
import unittest
from snewpdag.dag import Node

class TestBasicNode(unittest.TestCase):

  def setUp(self):
    self.n1 = Node('node1')
    self.n2 = Node('node2')
    self.n3 = Node('node3')
    self.n4 = Node('node4')

  def test_attach(self):
    self.n1.attach(self.n2)
    self.n1.attach(self.n3)
    self.n2.attach(self.n4)
    self.assertIn(self.n2, self.n1.observers)
    self.assertIn(self.n3, self.n1.observers)
    self.assertIn(self.n4, self.n2.observers)
    self.assertIn(self.n1, self.n2.watch_list)
    self.assertIn(self.n1, self.n3.watch_list)
    self.assertIn(self.n2, self.n4.watch_list)

    self.n1.detach(self.n3)
    self.assertIn(self.n2, self.n1.observers)
    self.assertNotIn(self.n3, self.n1.observers)
    self.assertIn(self.n4, self.n2.observers)
    self.assertIn(self.n1, self.n2.watch_list)
    self.assertNotIn(self.n1, self.n3.watch_list)
    self.assertIn(self.n2, self.n4.watch_list)

  def test_history(self):
    self.n1.attach(self.n2)
    self.n1.attach(self.n3)
    self.n2.attach(self.n4)
    data = { 'k': 'v' }
    self.n1.update(data)
    self.assertEqual(self.n1.last_data,
                     { 'k':'v', 'history':('node1',) })
    self.assertEqual(self.n2.last_data,
                     { 'k':'v', 'history':('node1','node2') })
    self.assertEqual(self.n3.last_data,
                     { 'k':'v', 'history':('node1','node3') })
    self.assertEqual(self.n4.last_data,
                     { 'k':'v', 'history':('node1','node2','node4') })

  def test_history_order(self):
    self.n1.attach(self.n3)
    self.n1.attach(self.n2)
    self.n3.attach(self.n4)
    data = { 'k': 'v' }
    self.n1.update(data)
    self.assertEqual(self.n1.last_data,
                     { 'k':'v', 'history':('node1',) })
    self.assertEqual(self.n2.last_data,
                     { 'k':'v', 'history':('node1','node2') })
    self.assertEqual(self.n3.last_data,
                     { 'k':'v', 'history':('node1','node3') })
    self.assertEqual(self.n4.last_data,
                     { 'k':'v', 'history':('node1','node3','node4') })

