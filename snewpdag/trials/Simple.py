"""
Generate a bunch of alerts/resets followed by a report signal.

This should be a stand-alone program streaming to stdout.
One line per json object.
Parameters:  number of objects, field, injection name

Generate 'alert' objects.
Close off with a 'report' object.
"""
import sys, argparse, json

def run():
  parser = argparse.ArgumentParser()
  parser.add_argument('name', help='injection name')
  parser.add_argument('-n', '--number', default=1000, help='number of trials')
  args = parser.parse_args()

  i = 0
  imax = int(args.number)
  while i < imax:
    print(json.dumps({ 'action': 'alert', 'burst_id': i, 'name': args.name }))
    print(json.dumps({ 'action': 'reset', 'burst_id': i, 'name': args.name }))
    i += 1
  print(json.dumps({ 'action': 'report', 'name': args.name }))

if __name__ == '__main__':
  run()

