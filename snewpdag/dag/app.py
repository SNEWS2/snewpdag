"""
SNEWPDAG application.

See README for details of the configuration and input data files.
"""

import sys, argparse
import json
import importlib
import logging

def run(argv):
  """
  Entrypoint for main application program.
  Takes positional command-line arguments:
    config - name of JSON configuration file
    input  - name of JSON input file
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('config', help='configuration JSON file')
  parser.add_argument('input', help='input data JSON file')
  args = parser.parse_args()

  with open(args.config) as f:
    nodespecs = json.loads(f.read())
  nodes = configure(nodespecs)

  with open(args.input) as f:
    data = json.loads(f.read())
  inject(nodes, data)

def configure(nodespecs):
  """
  Build DAG from configuration dictionary.
  """
  nodes = {}
  module = importlib.import_module('snewpdag.plugins')

  for spec in nodespecs:
    if 'class' in spec:
      c = getattr(module, spec['class'])
    else:
      logging.error('No class field in node specification')
      sys.exit(2)

    if 'name' in spec:
      name = spec['name']
    else:
      logging.error('No name field in node specification')
      sys.exit(2)

    if name in nodes:
      logging.error('Duplicate node name {}'.format(name))
      sys.exit(2)

    kwargs = spec['kwargs'] if 'kwargs' in spec else {}
    kwargs['name'] = spec['name']
    nodes[name] = c(**kwargs)

    if 'observe' in spec:
      for obs in spec['observe']:
        nodes[obs].attach(nodes[name])

  return nodes

def inject(nodes, data):
  """
  Send data through DAG.
  """
  for d in data:
    nodes[d['name']].update(d)

