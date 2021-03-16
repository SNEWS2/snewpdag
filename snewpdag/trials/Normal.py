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

def run():
  parser = argparse.ArgumentParser()
  parser.add_argument('name', help='injection name')
  parser.add_argument('-n', '--number', default=1000, help='number of trials')
  parser.add_argument('--mean', default=0.0, help='mean value')
  parser.add_argument('--rms', default=1.0, help='rms value')
  parser.add_argument('--field', default='x', help='field name to generate')
  parser.add_argument('--expt', default='Normal', help='experiment name')
  args = parser.parse_args()

  i = 0
  imax = int(args.number)
  mean = float(args.mean)
  rms = float(args.rms)
  rng = np.random.default_rng()
  while i < imax:
    data = { 'action': 'alert', 'name': args.name, 'id': i, 'expt': args.expt }
    data[args.field] = rng.normal(mean, rms)
    print(json.dumps(data))
    i += 1
  print(json.dumps({ 'action': 'report', 'name': args.name }))

if __name__ == '__main__':
  run()
