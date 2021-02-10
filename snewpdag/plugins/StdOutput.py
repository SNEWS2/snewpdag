"""
StdOutput:  print json to stdout

Just print the json of whatever this node receives.
"""
import json

from snewpdag.dag import Node

class StdOutput(Node):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)

  def update(self, data):
    print('**** {} ****'.format(self.name))
    self.print_dict('', data)
    print('---- {} ----'.format(self.name))
    self.notify(data['action'], None, data)

  def print_dict(self, indent, data):
    for k, v in data.items():
      if isinstance(v, dict):
        print('{0}{1}:'.format(indent, k))
        self.print_dict(indent + '  ', v)
      else:
        print('{0}{1}: {2}'.format(indent, k, v))

