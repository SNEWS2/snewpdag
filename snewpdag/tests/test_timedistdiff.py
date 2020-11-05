"""
Unit tests for TimeDistDiff node
"""
import unittest
import numpy as np
import healpy as hp
from snewpdag.dag import Node
from snewpdag.dag.app import configure, inject
from snewpdag.plugins import TimeDistFileInput, TimeDistDiff

class TestTimeDistDiff(unittest.TestCase):

  def test_inputs(self):
    #TimeDistDiffNode = TimeDistDiff(name='TimeDistDiffNode')
    TimeDistDiffNode = Node(name='TimeDistDiffNode')

    n1 = TimeDistFileInput(name='Input1')
    n2 = TimeDistFileInput(name='Input2')
    n1.attach(TimeDistDiffNode)
    n2.attach(TimeDistDiffNode)
    
    data = { 'action': 'alert',
             'filename': 'snewpdag/data/fluxparametrisation_22.5kT_0Hz_0.0msT0_1msbin.txt',
             'filetype': 'tn' }
    n1.update(data)

    data = { 'action': 'alert',
             'filename': 'snewpdag/data/fluxparametrisation_3500kT_1.548e+06Hz_0.0msT0_1msbin.txt',
             'filetype': 'tn' }
    n2.update(data)

    print(TimeDistDiffNode)
    print(TimeDistDiffNode.last_data['history'])
    self.assertListEqual(TimeDistDiffNode.last_data['history'], ('Input1','Input2'))
