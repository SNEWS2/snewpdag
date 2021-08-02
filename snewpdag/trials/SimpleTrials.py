"""
SimpleTrials - run MC trials directly into a DAG

This duplicates piping Simple.py output into the snewpdag module,
but without having to pipe in the shell.

spec can be constructed by hand, or by reading from a configuration file.

To read a python-formatted configuration file,

  from snewpdag.trials.SimpleTrials import trials
  import ast
  with open(filename, 'r') as f:
    spec = ast.literal_eval(f.read())
  trials(spec)

To read a csv-formatted configuration file,

  from snewpdag.trials.SimpleTrials import trials
  from snewpdag.dag.app import csv_eval
  with open(filename, 'r') as f:
    spec = csv_eval(f)
  trials(spec)
"""
import sys
from snewpdag.dag.app import configure, inject

def trials(spec, ntrials=1000):
  """
  Configure nodes using spec (a list of dictionaries).
  Then run alert/reset pairs for as many times as given in ntrials,
  followed by a report action.
  """
  nodes = configure(spec)
  if nodes == None:
    logging.error('Invalid configuration specified')
    return

  i = 0
  while i < ntrials:
    data = [ { 'action': 'alert', 'burst_id': i, 'name': 'Control' },
             { 'action': 'reset', 'burst_id': i, 'name': 'Control' } ]
    inject(nodes, data, spec)
    i += 1
  data = [ { 'action': 'report', 'name': 'Control' } ]
  inject(nodes, data, spec)

