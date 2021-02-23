"""
Unit tests for input classes.
"""
import unittest
import logging
import json
from snewpdag.dag import Node
from snewpdag.plugins import Shape

class TestShape(unittest.TestCase):

  def test_update(self):
    n1 = Shape(500, -0.2, 0.3, 5, -0.04, 0.0005, 160, 4, 0.01, 0, 0, name = 'Node1')
    n2 = Shape(500, -0.2, 0.3, 5, -0.04, 0.0005, 160, 4, 0.01, 1, 0.001, name = 'Node2')

    data = [ { 'name':'Input1', 'action': 'alert', 'times': [ -0.1, 0.11, 0.124, 0.122, 0.113, 0.1, 0.125, -0.15, -0.05, 0.24 ] },
            { 'name':'Input2', 'action': 'alert', 'times': [ -0.14, 0.15, 0.164, 0.162, 0.153, 0.14, 0.165, -0.11, -0.01, 0.28 ] } ]

    n1.update(data[0])
    n1.update(data[1])
    n2.update(data[0])
    n2.update(data[1])

