"""
DAG library routines
"""
import logging
import numbers
import numpy as np

# deprecated: ns_per_second
# deprecated: time_tuple_from_float(x)
# deprecated: time_tuple_from_offset(ns)
# deprecated: time_tuple_from_string(s)
# deprecated: time_tuple_from_field(s)
# deprecated: offset_from_time_tuple(tt)
# deprecated: normalize_time(a)
# deprecated: normalize_time_difference(a)
# deprecated: subtract_time(a, b)

def fetch_field(data, fields):
  """
  Fetch a field from the payload (data).
  If the field is a string, attempt to split by /'s.
    (Note: don't leave a trailing slash! It looks like an empty field name)
  If the field is list-like, interpret each element as the field name
    in each inner dictionary.
  Return value (or None), and True/False depending on field(s) existing.
  """
  fs = fields.split('/') if isinstance(fields, str) else fields
  if isinstance(fs, (list, tuple)):
    d = data
    for f in fs:
      if isinstance(d, dict) and f in d:
        d = d[f]
      elif isinstance(d, (list, tuple, np.ndarray)) and f < len(d):
        d = d[f]
      else:
        return None, False
    return d, True
  else:
    if fs in data:
      return data[fs], True
    else:
      return None, False

def store_field(data, field, value):
  fs = field.split('/') if isinstance(field, str) else field
  if isinstance(fs, (list, tuple)):
    d = data
    for f in fs[:-1]:
      if isinstance(d, dict) and f in d:
        d = d[f]
      else:
        d[f] = {}
        d = d[f]
    d[fs[-1]] = value
  else:
    data[fs] = value
  return True

def fill_filename(pattern, module_name, count, data):
  """
  Get filename, and fill out the details.
  pattern = '[field specifier]' - fetch pattern from payload using fetch_field.
    'filename' - use this literal string as the pattern.
  The pattern is filled as follows:
    {0} - module_name
    {1} - count
    {2} - data['burst_id']
  """
  ps = pattern.strip()
  if ps[0] == '[' and ps[-1] == ']':
    s, valid = fetch_field(data, ps[1:-1])
    if not valid:
      return None
    ps = s.strip()
  fn = ps.format(module_name, count, data.get('burst_id', 0))
  return fn

