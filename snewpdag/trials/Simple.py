"""
Generate a bunch of alerts/resets followed by a report signal.

This should be a stand-alone program streaming to stdout.
One line per json object.
Parameters:  number of objects, field, injection name

Generate 'alert' objects.
Close off with a 'report' object.

Note that trial_id keeps track of which trial is being run.
burst_id is always 0.  The reason for this is that a new burst_id
would trigger inject() to create a new DAG from scratch.
So we keep burst_id the same, but count using trial_id.
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
    print(json.dumps(
      { 'action': 'alert', 'burst_id': 0, 'trial_id': i, 'name': args.name }))
    print(json.dumps(
      { 'action': 'reset', 'burst_id': 0, 'trial_id': i, 'name': args.name }))
    i += 1
  print(json.dumps({ 'action': 'report', 'burst_id': 0, 'name': args.name }))

if __name__ == '__main__':
  run()

