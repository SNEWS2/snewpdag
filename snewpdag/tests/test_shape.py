"""
Unit tests for input classes.
"""
import unittest
import logging
from snewpdag.dag import Node
from snewpdag.plugins import Shape

class TestShape(unittest.TestCase):

  def test_update(self):
    n1 = Shape(name = "Node1", 500, -0.2, 0.3, 5, -0.04, 0.0005, 160, 4, 0.01, 0, 0)
    n2 = Shape(name = "Node2", 500, -0.2, 0.3, 5, -0.04, 0.0005, 160, 4, 0.01, 1, 0.001)
    n1.attach(Node('Node1'))
    n2.attach(Node('Node2'))

    data = [ { 'action': 'alert', 'times': [ -0.1, 0.11, 0.124, 0.122, 0.113, 0.1, 0.125, -0.15, -0.05, 0.24 ] },
             { 'action': 'alert', 'times': [ -0.14, 0.15, 0.164, 0.162, 0.153, 0.14, 0.165, -0.11, -0.01, 0.28 ] } ]

    n1.update(data)
    n2.update(data)

