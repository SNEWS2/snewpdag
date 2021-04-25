import matplotlib.pyplot as plt
import unittest
import logging
from snewpdag.dag import Node
from snewpdag.plugins import TimeDistFileInput, TimeDistDiff, TimeSeriesInput
import matplotlib.pyplot as plt
import numpy as np
import json


class TestGenerateJSON(unittest.TestCase):

  def test_inputs(self):

      file_name = "27_Shen_1D_solar_mass_progenitor.fits"
      f1 = "/home/mcolomer/snewpy_clone/snewpy/data/output_icecube_"+file_name+"_1secdur_1msbin.txt"

      OutputNode = Node(name='Output')
      TimeDistDiffNode = TimeDistDiff(name='TimeDistDiffNode')                                                                                                                         
      n1 = TimeDistFileInput(name='Input1')
      n1.attach(TimeDistDiffNode)
      TimeDistDiffNode.attach(OutputNode)

      data = { 'action': 'alert',
               'filename': f1,
               'filetype': 'tn' }
      n1.update(data)
      fout1 = open("/home/mcolomer/SNEWS/snewpdag/snewpdag/data/output_icecube_"+file_name+"_1secdur_1msbin.json",'w')
      out_data = []
      out_data.append({
        'name': 'icecube',
        'action': 'alert',
        'model': file_name,
        'binning': '1 ms',
        'duration:' '1 sec'
        'comment': '0Hz background',
        't': data['t'],
        'n': data['n']
      })
      out_data = json.dumps(out_data,indent=1)
      print(out_data, file=fout1)

  def test_experiments(self):
    
      file_name = "27_Shen_1D_solar_mass_progenitor.fits"
      fin = "/home/mcolomer/snewpy_clone/snewpy/data/output_icecube_"+file_name+"_1secdur_1msbin.txt"    
      #OutputNode = Node(name='Output')
      #TimeDistDiffNode = TimeDistDiff(name='TimeDistDiffNode')
      #n1 = TimeDistFileInput(name='Input1')
      #n1.attach(TimeDistDiffNode)
      #TimeDistDiffNode.attach(OutputNode)

      #data = { 'action': 'alert',
      #         'filename': fin,
      #         'filetype': 'tn' }
      #n1.update(data)

      json_file = open("/home/mcolomer/SNEWS/snewpdag/snewpdag/data/output_icecube_"+file_name+"_1secdur_1msbin.json",'r')
      print(json_file)
      data = json.load(json_file)
      #print(data[0]['t'])
      data = data[0]
      
      t0  = 100
      new_times = np.arange(-2,8,0.001)
      print(new_times)
      new_data = []
      bg_mean = 1548 #total bg events per ms
      for j,t in enumerate(new_times):
        bg = np.random.poisson(bg_mean)
        #print(t,j,j-2001, data['t'][-1]-0.001)
        if t>t0/1000. and t<data['t'][-1]-0.001:
          print(t,j,j-2001, data['t'][-1]-0.001)
          signal = np.random.poisson(data['n'][j-t0-2001])
          new_data.append(signal+bg)
        else:
          new_data.append(bg)
      
      plt.rcParams.update({'font.size': 14})
      plt.plot(new_times,new_data,label='IceCube')
      #plt.yscale('log')   
      plt.xlim(-2,3)
      plt.ylabel('Events per ms', size=16)
      plt.xlabel('Time [ms]', size=16)
      plt.show()
      
