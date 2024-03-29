"""
JsonAlertInput - read json from a file to form one alert.

Arguments:
  filename - path to data file. Can include {} for the counter.

The file contents are read and added to the payload.
Note that the action field cannot be overwritten.
"""
import logging
import json
import sys

from snewpdag.dag import Node
from snewpdag.dag.lib import fill_filename

class JsonAlertInput(Node):
  def __init__(self, filename, **kwargs):
    self.filename = filename
    self.count = 0
    super().__init__(**kwargs)

  def alert(self, data):
    fname = fill_filename(self.filename, self.name, self.count, data)
    if fname == None:
      logging.error('{}: error interpreting {}', self.name, self.filename)
      return False
    try:
      with open(fname, 'r') as f:
        #d = ast.literal_eval(f.read())
        d = json.load(f)
    except:
      logging.error('{}: exception while reading file {}: {}'.format( \
          self.name, self.filename.format(self.count), sys.exc_info()))
      return False
    # don't overwrite action
    if 'action' in d:
      d['action'] = data['action']
    data.update(d)
    self.count += 1
    return data

