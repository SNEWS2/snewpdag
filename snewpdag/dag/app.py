"""
SNEWPDAG application.

See README for details of the configuration and input data files.
"""

import os, sys, argparse, json, logging, importlib, ast, csv
import numpy as np
from . import Node

parser = argparse.ArgumentParser()
parser.add_argument('config', help='configuration py/json/csv file')
parser.add_argument('--input', help='input data py/json file')
parser.add_argument('--jsonlines', action='store_true', help='each input line contains one JSON object to inject')
parser.add_argument('--log', help='logging level')
parser.add_argument('--seed', help='random number seed')
parser.add_argument('--stream', help="read from the hop alert stream server")
args = parser.parse_args()
if args.stream:
  try:
    from hop import stream
  except:
    logging.info('Cannot import the hop client')
    pass

# Possibly use snews_pt subscribe method in a near future
def save_message(message, counter):
  """ Save hop alert messages to a json file.
  """
  path = f'SNEWS_MSGs/'
  os.makedirs(path, exist_ok=True)
  file = path + 'subscribed_messages.json'
  # read the existing file
  try:
    data = json.load(open(file))
    if not isinstance(data, dict):
      print('Incompatible file format!')
      return None

  except:
    data = {}

  # Adding fields to the alert message (which are needed to run the dags)
  #### This parameters will be changed based on the actual alert message sent from the hop stream
  index_coincidence = str(counter) # In reality, this has to be read from the hop alert message
  if message['_id'].split("_")[3] == 'ALERT': # to change
    message['action'] = 'alert'
  message['name'] = 'Control' # keep this
  message['number_of_coinc_dets'] = len(message['detector_names']) # keep this
  message['coinc_id'] = 'coinc' + index_coincidence # In reality, this has to be read from the message
  data['coinc' + index_coincidence] = message

  with open(file, 'w') as outfile:
    json.dump(data, outfile)


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
  # use a local kafka topic, check the environment file of snews_pt for running online
  alert_topic = "kafka://localhost:9092/snews.alert-test"
  #alert_topic = "kafka://kafka.scimma.org/snews.alert-test" ## online alert topic for reading alerts. To use this you need credentials

  counter = 0 # keep track of the number of coincidence, in reality, this has to be read from the hop alert message

  if args.log:
    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
      raise ValueError('Invalid log level {}'.format(args.log))
    logging.basicConfig(level=numeric_level)

  # initialize random number generator
  if args.seed:
    Node.rng = np.random.default_rng(int(args.seed))
  else:
    Node.rng = np.random.default_rng()

  cfn, cfx = os.path.splitext(args.config)
  if cfx == '.csv':
    # name, class, observe
    with open(args.config, 'r') as f:
      nodespecs = csv_eval(f)
  else: # try python/json parsing if not csv
    with open(args.config, 'r') as f:
      nodespecs = ast.literal_eval(f.read())
    #nodes = configure(nodespecs)

  dags = {}

  if args.input:
    with open(args.input) as f:
      if args.jsonlines:
        for jsonline in f:
          data = ast.literal_eval(jsonline)
          inject(dags, data, nodespecs, counter)
      else:
        data = ast.literal_eval(f.read())
        inject(dags, data, nodespecs, counter)

  elif args.stream:
      s = stream.open(alert_topic, "r")
      for message in s:
        counter +=1 ### which coincidence is this? # In reality, this has to be read from the hop alert message
        index_coincidence = str(counter)
        save_message(message, counter)
        with open('SNEWS_MSGs/subscribed_messages.json') as f:
          data = ast.literal_eval(f.read())
          # Iinjecting this data into a dag:
          inject(dags, data['coinc' + index_coincidence], nodespecs, counter)
  else:
    if args.jsonlines:
      for jsonline in sys.stdin:
        data = ast.literal_eval(jsonline)
        inject(dags, data, nodespecs, counter)
    else:
      data = ast.literal_eval(sys.stdin.read())
      inject(dags, data, nodespecs, counter)

def csv_eval(infile):
  # name, class, observe
  nodespecs = []
  reader = csv.reader(infile, quotechar='"')
  for row in reader:
    #print('New row:  {}'.format(row))
    if len(row) == 0:
      continue # blank line
    if row[0] == '' or row[0][0] == '#':
      continue # comment line
    if len(row) < 2:
      logging.error('Node specification requires at least 2 fields')
      continue
    node = { 'name': row[0], 'class': row[1] }
    if len(row) >= 3 and len(row[2]) > 0:
      nl = []
      ns = row[2].strip().split(',')
      for n in ns:
        s = n.strip()
        if len(s) > 0:
          nl.append(s)
      node['observe'] = nl
    if len(row) >= 4:
      s = []
      for i in range(3, len(row)):
        if len(row[i]) > 0:
          # replace special marks which might stand in for single quotes
          r = row[i].replace("’","'").replace("‘","'").replace("`","'")
          s.append(r)
      node['kwargs'] = ast.literal_eval('{' + ','.join(s) + '}')
    nodespecs.append(node)
  return nodespecs

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
      return None

    if 'name' in spec:
      name = spec['name']
    else:
      logging.error('No name field in node specification')
      return None

    if name in nodes:
      logging.error('Duplicate node name {}'.format(name))
      return None

    kwargs = spec['kwargs'] if 'kwargs' in spec else {}
    kwargs['name'] = spec['name']
    try:
      nodes[name] = c(**kwargs)
    except TypeError:
      logging.error('While creating node {0}: {1}'.format(name, sys.exc_info()))
      return None

    if 'observe' in spec:
      for obs in spec['observe']:
        if obs == name:
          logging.error('{0} observing itself'.format(name))
          return None
        elif obs in nodes:
          nodes[obs].attach(nodes[name])
        else:
          logging.error('{0} observing unknown node {1}'.format(name, obs))
          return None

  return nodes

def inject(dags, data, nodespecs, counter):
  """
  Send data through DAG.
  If there is no burst identifier, assume it's 0.
  If the DAG doesn't exist for this coincidence, create a new one.
  """
  if type(data) is dict:
    inject_one(dags, data, nodespecs, counter)
  elif type(data) is list:
    for d in data:
      inject_one(dags, d, nodespecs, counter)

  else:
    logging.error('What is this input data?')
    sys.exit(2)

def inject_one(dags, data, nodespecs, counter):
  index_coincidence = str(counter) # In reality, this has to be read from the hop alert message
  if 'dag_coinc' + index_coincidence not in dags: # e.g. dag_coinc1, dag_coinc2
    dags['dag_coinc' + index_coincidence] = configure(nodespecs)
  dag = dags['dag_coinc' + index_coincidence]
  dag[data['name']].update(data)

