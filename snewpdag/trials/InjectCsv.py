"""
Generate messages from a csv file.

By default, actions are alert, burst_id = 0, and trial_id counts the messages.
However, these can be overridden by the csv file.

Note that this doesn't automatically emit reset or report messages,
so if you want those you need to put them in your csv file.

Format of the csv file:
* First line is the header, each column giving a key name.
  As noted above, action, burst_id, and trial_id can be overridden;
  if you want to do so, write "action", "burst_id", and/or "trial_id" in
  a column in this first line.
* Subsequent lines are for each message.
  Empty lines (all fields blank) are ignored.
  Empty fields are also ignored, and those fields not written into the
  message.  This means that if you like to override "action", you can
  leave it blank to get the default "alert" value.

burst_id should be left as 0.
The reason for this is that a new burst_id
would trigger inject() to create a new DAG from scratch.
So we usually keep burst_id the same, but count using trial_id.
"""
import sys, argparse, json, csv

def run():
  parser = argparse.ArgumentParser()
  parser.add_argument('name', help='injection name')
  parser.add_argument('input', help='csv file to inject')
  args = parser.parse_args()

  count = 0
  first = True
  with open(args.input, 'r') as f:
    cr = csv.reader(f)
    for row in cr:
      if first:
        keys = row
        first = False
      else:
        # check if row is empty
        if sum([len(v) for v in row]) == 0:
          continue

        # construct alert message (empty fields ignored)
        d = { 'action': 'alert', 'burst_id': 0, 'trial_id': count,
              'name': args.name }
        for i in range(min(len(keys),len(row))):
          if len(row[i]) > 0:
            d[keys[i]] = row[i]
        print(json.dumps(d))

        # inject reset message
        #print(json.dumps(
        #  { 'action': 'reset', 'burst_id': 0, 'trial_id': count,
        #    'name': args.name }))
        count += 1

  #print(json.dumps({ 'action': 'report', 'burst_id': 0, 'name': args.name }))

if __name__ == '__main__':
  run()

