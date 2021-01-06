"""
Unit tests for TimeDistDiff node
"""
import unittest
import numpy as np
import healpy as hp
from snewpdag.dag import Node
from snewpdag.dag.app import configure, inject
from snewpdag.plugins import TimeDistFileInput, TimeDistDiff

import os

class TestTimeDistDiff(unittest.TestCase):

  def test_inputs(self):
    OutputNode = Node(name='Output')
    TimeDistDiffNode = TimeDistDiff(name='TimeDistDiffNode')
    #TimeDistDiffNode = Node(name='TimeDistDiffNode')

    n1 = TimeDistFileInput(name='Input1')
    n2 = TimeDistFileInput(name='Input2')
    n1.attach(TimeDistDiffNode)
    n2.attach(TimeDistDiffNode)
    TimeDistDiffNode.attach(OutputNode)

    
    os.system('externals/lightcurve_match/simulation/detectorrate 3500 1548000 0') #IC
    os.system('externals/lightcurve_match/simulation/detectorrate 22.5 0 0') #SK
    
    data = { 'action': 'alert',
             'filename': 'fluxparametrisation_22.5kT_0Hz_0.0msT0_1msbin.txt',
             'filetype': 'tn' }
    n1.update(data)

    data = { 'action': 'alert',
             'filename': 'fluxparametrisation_3500kT_1.548e+06Hz_0.0msT0_1msbin.txt',
             'filetype': 'tn' }
    n2.update(data)

    self.assertEqual(OutputNode.last_data['history'], (('Input1',), ('Input2',), 'TimeDistDiffNode', 'Output'))
    print(OutputNode.last_data['tdelay'])

  def test_many(self):
      tdelayarr = []
      for i in range(1,10):
        OutputNode = Node(name='Output')
        TimeDistDiffNode = TimeDistDiff(name='TimeDistDiffNode')
        #TimeDistDiffNode = Node(name='TimeDistDiffNode')

        n1 = TimeDistFileInput(name='Input1')
        n2 = TimeDistFileInput(name='Input2')
        n1.attach(TimeDistDiffNode)
        n2.attach(TimeDistDiffNode)
        TimeDistDiffNode.attach(OutputNode)

        
        os.system('externals/lightcurve_match/simulation/detectorrate 3500 1548000 0') #IC
        #os.system('externals/lightcurve_match/simulation/detectorrate 22.5 0 0') #SK
        data = { 'action': 'alert',
                 'filename': 'fluxparametrisation_3500kT_1.548e+06Hz_0.0msT0_1msbin.txt',
                 #'filename': 'fluxparametrisation_22.5kT_0Hz_0.0msT0_1msbin.txt',
                 'filetype': 'tn' }
        n1.update(data)

        os.system('externals/lightcurve_match/simulation/detectorrate 22.5 0 0') #SK
        data = { 'action': 'alert',
                 'filename': 'fluxparametrisation_22.5kT_0Hz_0.0msT0_1msbin.txt',
                 'filetype': 'tn' }
        n2.update(data)

        tdelayarr.append(OutputNode.last_data['tdelay'][('Input1', 'Input2')][0])
        print("toy: ", i, "deltaT:", tdelayarr[-1]*1000,"ms")
      print("mean [ms], rms [ms]", np.mean(tdelayarr)*1000, np.std(tdelayarr)*1000)
