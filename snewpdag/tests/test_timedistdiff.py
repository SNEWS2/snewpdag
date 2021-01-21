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

    
    os.system('externals/lightcurve_match/simulation/detectorrate 3500 1548000 0 0.1') #IC
    os.system('externals/lightcurve_match/simulation/detectorrate 22.5 0 0 0.1') #SK
    
    data = { 'action': 'alert',
             'filename': 'fluxparametrisation_22.5kT_0Hz_0.0msT0_0.1msbin.txt',
             'filetype': 'tn' }
    n1.update(data)

    data = { 'action': 'alert',
             'filename': 'fluxparametrisation_3500kT_1.548e+06Hz_0.0msT0_0.1msbin.txt',
             'filetype': 'tn' }
    n2.update(data)

    self.assertEqual(OutputNode.last_data['history'], (('Input1',), ('Input2',), 'TimeDistDiffNode', 'Output'))
    print(OutputNode.last_data['tdelay'])

  def test_many(self):
      tdelayarr = []
      tdelaycpparr = []
      for i in range(1,10):
        OutputNode = Node(name='Output')
        TimeDistDiffNode = TimeDistDiff(name='TimeDistDiffNode')
        #TimeDistDiffNode = Node(name='TimeDistDiffNode')

        n1 = TimeDistFileInput(name='Input1')
        n2 = TimeDistFileInput(name='Input2')
        n1.attach(TimeDistDiffNode)
        n2.attach(TimeDistDiffNode)
        TimeDistDiffNode.attach(OutputNode)

        
        os.system('externals/lightcurve_match/simulation/detectorrate 3500 1548000 0.01 0.1') #IC
        data = { 'action': 'alert',
                 'filename': 'fluxparametrisation_3500kT_1.548e+06Hz_10.0msT0_0.1msbin.txt',
                 'filetype': 'tn' }
        n1.update(data)

        os.system('externals/lightcurve_match/simulation/detectorrate 22.5 0 0 0.1') #SK
        data = { 'action': 'alert',
                 'filename': 'fluxparametrisation_22.5kT_0Hz_0.0msT0_0.1msbin.txt',
                 'filetype': 'tn' }
        n2.update(data)

        tdelayarr.append(OutputNode.last_data['tdelay'][('Input1', 'Input2')][0])

        p1 = os.popen('./externals/lightcurve_match/matching/getdelay fluxparametrisation_3500kT_1.548e+06Hz_10.0msT0_0.1msbin.txt fluxparametrisation_22.5kT_0Hz_0.0msT0_0.1msbin.txt  chi2 50 50 -300 300 -100 100 0.1 | grep T0match | cut -f 2 -d " "')
        tdelycpp  = p1.read()
        p1.close()
        tdelycppint = float(tdelycpp)
        tdelaycpparr.append(-tdelycppint)
        print("toy: ", i, "deltaT:", tdelayarr[-1]*1000,"ms", "chi2",OutputNode.last_data['tdelay'][('Input1', 'Input2')][1], "deltaT cpp:", tdelaycpparr[-1],"ms")
        print("Det1-Det2 delay python mean [ms], rms [ms]", float(np.mean(tdelayarr)*1000), float(np.std(tdelayarr)*1000))
        print("Det1-Det2 delay cpp    mean [ms], rms [ms]", float(np.mean(tdelaycpparr)), float(np.std(tdelaycpparr)))


      mean = float(np.mean(tdelayarr)*1000)
      rms = float(np.std(tdelayarr)*1000)
      print("Det1-Det2 delay mean [ms], rms [ms]", mean, rms)
      self.assertTrue( (10 - rms < mean) & (mean< 10 + rms) )
      self.assertTrue( rms < 10)

      meancpp = float(np.mean(tdelaycpparr))
      rmscpp = float(np.std(tdelaycpparr))
      print("Det1-Det2 delay from cpp mean [ms], rms [ms]", meancpp, rmscpp)
