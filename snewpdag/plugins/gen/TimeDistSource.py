"""
TimeDistSource:  root class for time histogram-based generators

configuration:
  filename:  histogram file name
  filetype:  'tn' -> csv file of time (low edge of bin), number of events
                     (the last bin is excluded because one needs a high edge)
             'json' -> python-literal dictionary with t and n arrays,
                       or n array with tmin, tmax values
                       (tmax is high edge of last bin)

output added to data:
  't': low edges of time bins (array of floats).
       This will have one more element than the 'n' array;
       the last element will be the high edge of the last bin.
  'n': number of events in corresponding time bins (array of floats)

If update is called, the histogram is copied into the data dictionary.
"""
import sys
import logging
import csv
import ast
import numpy as np

from snewpdag.dag import Node

class TimeDistSource(Node):

  def __init__(self, filename, filetype, **kwargs):
    if filetype == 'tn':
      tt = []
      nn = []
      with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
          tt.append(float(row[0]))
          nn.append(float(row[1]))
      self.t = np.array(tt)
      # use the last bin edge as the maximum.
      # This amounts to cutting off the last n element.
      self.mu = np.array(nn[:-1])
    else:
      with open(filename, 'r') as f:
        data = ast.literal_eval(f.read())
      if 'n' in data:
        if 'tmin' in data and 'tmax' in data:
          n = data['n']
          dt = (data['tmax'] - data['tmin']) / len(n)
          # end of range specified such that last element is tmax
          self.mu = np.array(n)
          self.t = np.arange(data['tmin'], data['tmax'] + dt, dt)
        elif 'n' in data and 't' in data:
          nn = data['n']
          tt = data['t']
          if len(tt) <= len(nn):
            # truncate nn to length
            del nn[len(tt)-1:]
          elif len(tt) > len(nn) + 1:
            del tt[len(nn)+1:]
          self.mu = np.array(nn)
          self.t = np.array(tt)
        else:
          logging.error('Unrecognized field combinations for json histogram.')
          sys.exit(2)
      else:
        logger.error('No n field in histogram.')
        sys.exit(2)
    super().__init__(**kwargs)

  def alert(self, data):
    data['t'] = self.t.copy()
    data['n'] = self.mu.copy()
    return True

