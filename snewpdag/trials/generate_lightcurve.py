"""
Generate a normal distribution as a test input.

This should be a stand-alone program streaming to stdout.
One line per json object.
Parameters:  number of objects, mean, rms, field, injection name

Generate 'alert' objects.
Close off with a 'report' object.
"""
import sys, argparse, json
import numpy as np

def generate_pseudoexp():
  parser = argparse.ArgumentParser()
  parser.add_argument('-n', '--number', default=10, help='number of trials')
  parser.add_argument('--mean', default=0.0, help='mean value')
  args = parser.parse_args()

  i = 0
  imax = int(args.number)

  file_name = "27_Shen_1D_solar_mass_progenitor.fits"
  json_file = open("/home/mcolomer/SNEWS/snewpdag/snewpdag/data/output_icecube_"+file_name+"_1secdur_1msbin.json",'r')
  print(json_file)
  data = json.load(json_file)
  #print(data[0]['t'])                                                                                                                                                  
  data = data[0]
  bg_mean = 1548 #total bg events per ms

  while i<imax:
      print(i)
      new_times = np.arange(-2,8,0.001)
      t0 = int(np.random.uniform(-20,20))
      print(t0)
      new_data = []

      for j,t in enumerate(new_times):
        bg = np.random.poisson(bg_mean)
        #print(t,j,j-2001, data['t'][-1]-0.001)                                                                                                                        
        if t>t0/1000. and t<data['t'][-1]-0.001+t0/1000.:
          #print(t0, t, j , j-t0-2001, data['t'][-1]-0.001+t0/1000.)
          signal = np.random.poisson(data['n'][j-t0-2001])
          new_data.append(signal+bg)
        else:
          new_data.append(bg)
      fout1 = open("/home/mcolomer/snewpdag/snewpdag/data/output_icecube_"+file_name+"_1secdur_1msbin_PE"+str(i)+".json",'w')
      out_data = []
      out_data.append({
        'name': 'icecube',
        'action': 'alert',
        'model': file_name,
        'binning': '1 ms',
        'duration:' '1 sec'
        'comment': '1548 mHz background',
        't': list(new_times),
        'n': new_data
      })

      #print(data['n'])
      #print(new_data)
      out_data = json.dumps(out_data,indent=1)
      print(out_data, file=fout1)
      i+=1
  #plt.rcParams.update({'font.size': 14})
  #plt.plot(new_times,new_data,label='IceCube')
  #plt.yscale('log')                                                                                                                                                                                     
  #plt.xlim(-2,3)
  #plt.ylabel('Events per ms', size=16)
  #plt.xlabel('Time [ms]', size=16)
  #plt.show()


  #data = { 'action': 'alert', 'name': args.name }
  #data[args.field] = rng.normal(mean, rms)
  #print(json.dumps(data))
  #i += 1
  #print(json.dumps({ 'action': 'report', 'name': args.name }))

if __name__ == '__main__':
  generate_pseudoexp()
