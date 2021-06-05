"""
TimeDistSource:  root class for time histogram-based generators

configuration:
  sig_filename:  histogram file name
  sig_filetype:  'tn' -> csv file of time (low edge of bin), number of events
                     (the last bin is excluded because one needs a high edge)
                'json' -> python-literal dictionary with
                     sig_t_low, sig_t_high, sig_t_bins

output added to data:
  gen: this is a tuple containing references to generated data.
       The generated dictionary has the following fields:
    'gen_sig_t_low': low edges of time bins (nd.array)
    'gen_sig_t_high':  high edge of the last time bin
    'gen_sig_t_bins': number of events in corresponding time bins (nd.array)
  After all the generators have run, a concatenator needs to
  string all the output together into either a series or distribution.

If update is called, the histogram is copied into the data dictionary.
"""
import sys
import logging
import csv
import ast
import numbers
import numpy as np

from snewpdag.dag import Node

class TimeDistSource(Node):

  def __init__(self, sig_filename, sig_filetype, **kwargs):
    if sig_filetype == 'tn':
      tt = []
      nn = []
      with open(sig_filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
          tt.append(float(row[0]))
          nn.append(float(row[1]))
      self.t = np.array(tt[:-1])
      self.thi = tt[-1]
      # use the last bin edge as the maximum.
      # This amounts to cutting off the last n element.
      self.mu = np.array(nn[:-1])
    else:
      with open(sig_filename, 'r') as f:
        data = ast.literal_eval(f.read())
      if 'sig_t_bins' in data and 'sig_t_low' in data and 'sig_t_high' in data:
        nn = data['sig_t_bins']
        self.mu = np.array(nn)
        self.mu.flags.writeable = False
        self.thi = data['sig_t_high']
        tt = data['sig_t_low']
        if isinstance(tt, numbers.Number):
          dt = (data['sig_t_high'] - tt) / len(nn)
          self.t = np.arange(tt, data['sig_t_high'] + dt, dt)
          self.t.flags.writeable = False
        elif isinstance(tt, (list, tuple)):
          if len(tt) != len(nn):
            logging.error('Lengths of sig_t_bins and sig_t_low do not match')
            sys.exit(2)
          self.t = np.array(tt)
          self.t.flags.writeable = False
        else:
          logging.error('Unrecognized sig_t_low type')
          sys.exit(2)
      else:
        logger.error('Missing histogram fields')
        sys.exit(2)
    super().__init__(**kwargs)

  def alert(self, data):
    ngen = { 'gen_sig_t_bins': self.mu, # immutable
             'gen_sig_t_low': self.t, # immutable
             'gen_sig_t_high': self.thi }
    if 'gen' in data:
      data['gen'] += (ngen, )
    else:
      data['gen'] = (ngen, )
    return True

