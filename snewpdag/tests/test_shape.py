"""
Unit tests for input classes.
"""
import unittest
import logging
import json
from snewpdag.dag import Node
from snewpdag.plugins import ShapeComparison
from snewpdag.plugins import ShapeHist
from snewpdag.plugins import BayesianBlocks

class TestShape(unittest.TestCase):

  def test_update(self):
    shapehist = ShapeHist(500, -0.2, 0.3)
    shape = ShapeComparison(shapehist, 5.0, -0.04, 0.0005, 160, 4, 0.01, name = 'Node1')
    bayes = BayesianBlocks(shapehist, shape, 0.001, 0.03, name = 'Node2')

    data = [ { 'name':'Input1', 'action': 'alert', 'times': [ -0.1, 0.11, 0.124, 0.122, 0.113, 0.1, 0.125, -0.15, -0.05, 0.24 ] },
            { 'name':'Input2', 'action': 'alert', 'times': [ -0.08, 0.13, 0.144, 0.142, 0.133, 0.12, 0.145, -0.13, -0.03, 0.26 ] } ]

    shape.update(data[0])
    shape.update(data[1])

    bayes.update(data[0])
    bayes.update(data[1])

