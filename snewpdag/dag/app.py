"""
SNEWPDAG application.

See README for details of the configuration and input data files.
"""

import sys, argparse
import json
import importlib
import logging

def run():
  """
  Entrypoint for main application program.
  Takes positional command-line arguments:
    config - name of JSON configuration file
    input  - name of JSON input file

  With the --jsonlines option, read from stdin assuming one json object/line.
  I know, this kind of sucks, but the alternative is importing another
  third-party module which provides more functionality than is needed here.
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('config', help='configuration JSON file')
  parser.add_argument('--input', help='input data JSON file')
  parser.add_argument('--jsonlines', action='store_true',
                      help='each input line contains one JSON object to inject')
  parser.add_argument('--log', help='logging level')
  args = parser.parse_args()

  if args.log:
    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
      raise ValueError('Invalid log level {}'.format(args.log))
    logging.basicConfig(level=numeric_level)

  with open(args.config) as f:
    nodespecs = json.loads(f.read())
  #nodes = configure(nodespecs)

  dags = {}

  if args.input:
    with open(args.input) as f:
      if args.jsonlines:
        for jsonline in f:
          data = json.loads(jsonline)
          inject(dags, data, nodespecs)
      else:
        data = json.loads(f.read())
        inject(dags, data, nodespecs)
  else:
    if args.jsonlines:
      for jsonline in sys.stdin:
        data = json.loads(jsonline)
        inject(dags, data, nodespecs)
    else:
      data = json.loads(sys.stdin.read())
      inject(dags, data, nodespecs)

def find_class(name):
  s = name.split('.')
  base = ['snewpdag','plugins']
  path = '.'.join(base+s[0:-1])
  cl = s[-1]
  mod = importlib.import_module(path)
  if hasattr(mod, cl):
    return getattr(mod, cl)
  else:
    logging.error('Unknown class {} in {}'.format(cl, path))
    sys.exit(2)

def configure(nodespecs):
  """
  Build DAG from configuration dictionary.
  """
  nodes = {}

  for spec in nodespecs:
    if 'class' in spec:
      c = find_class(spec['class'])
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
    try:
      nodes[name] = c(**kwargs)
    except TypeError:
      logging.error('While creating node {0}: {1}'.format(name, sys.exc_info()))
      sys.exit(2)

    if 'observe' in spec:
      for obs in spec['observe']:
        if obs in nodes:
          nodes[obs].attach(nodes[name])
        else:
          logging.error('{0} observing unknown node {1}'.format(name, obs))
          sys.exit(2)

  return nodes

def inject(dags, data, nodespecs):
  """
  Send data through DAG.
  If there is no burst identifier, assume it's 0.
  If the DAG doesn't exist for this burst, create a new one.
  """
  if type(data) is dict:
    inject_one(dags, data, nodespecs)
  elif type(data) is list:
    for d in data:
      inject_one(dags, d, nodespecs)
  else:
    logging.error('What is this input data?')
    sys.exit(2)

def inject_one(dags, data, nodespecs):
  burst_id = 0
  if 'burst_id' in data:
    burst_id = data['burst_id']
  if burst_id not in dags:
    dags[burst_id] = configure(nodespecs)
  dag = dags[burst_id]
  dag[data['name']].update(data)

