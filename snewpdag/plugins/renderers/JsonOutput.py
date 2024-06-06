"""
JsonOoutput - dump a dictionary made of specified fields into a json file

Arguments:
  fields: list of strings or tuples, list of fields to be copied into dictionary
  filename:  output filename, with fields
             {0} renderer name
             {1} count index, starting from 0
             {2} burst_id from update data (default 0 if no such field)
  on (optional): list of 'alert', 'reset', 'revoke', 'report'
    (default ['alert'])

To load json file at python prompt:

import json
with open(filename, 'r') as f:
  d = json.load(f)
"""
import logging
import json
import numbers
import numpy as np

from snewpdag.dag import Node
from snewpdag.values import TimeSeries
from snewpdag.dag.lib import fetch_field, fill_filename

def json_output_default(obj):
  if isinstance(obj, np.ndarray):
    return [ x for x in obj ]
  elif isinstance(obj, TimeSeries):
    return obj.to_dict()
  elif isinstance(obj, numbers.Number):
    return float(obj)
  else:
    raise TypeError("unjsonable type {}".format(obj))

class JsonOutput(Node):
  def __init__(self, fields, filename, **kwargs):
    self.fields = fields
    self.filename = filename
    self.on = kwargs.pop('on', ['alert'])
    self.count = 0
    super().__init__(**kwargs)

  def write_json(self, data):
    d = {}
    for f in self.fields:
      v, flag = fetch_field(data, f)
      if flag:
        #if isinstance(v, TimeSeries):
        #  d[f] = v.to_dict()
        #elif isinstance(v, np.ndarray):
        #  d[f] = [ x for x in v ]
        #else:
        d[f] = v
    #logging.info('{}: dict = {}'.format(self.name, d))

    fname = fill_filename(self.filename, self.name, self.count, data)
    if fname == None:
      logging.error('{}: error interpreting {}'.format(self.name, self.filename))
    else:
      logging.info('{}: writing json to {}'.format(self.name, fname))
      with open(fname, "w") as outfile:
        json.dump(d, outfile, default=json_output_default)

      self.count += 1
    return True

  def alert(self, data):
    return self.write_json(data) if 'alert' in self.on else True

  def revoke(self, data):
    return self.write_json(data) if 'revoke' in self.on else True

  def reset(self, data):
    return self.write_json(data) if 'reset' in self.on else True

  def report(self, data):
    return self.write_json(data) if 'report' in self.on else True

