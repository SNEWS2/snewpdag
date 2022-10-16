"""
DAG library routines
"""
import logging
import numbers
import numpy as np
from astropy.time import Time

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
  If the field is not list-like, then just get it directly.
  If the field is list-like, interpret each element as the field name
    in each inner dictionary.
  Return value (or None), and True/False depending on field(s) existing.
  """
  if isinstance(fields, (list, tuple)):
    d = data
    for f in fields:
      if isinstance(d, dict) and f in d:
        d = d[f]
      elif isinstance(d, (list, tuple, np.ndarray)) and f < len(d):
        d = d[f]
      else:
        return None, False
    return d, True
  else:
    if fields in data:
      return data[fields], True
    else:
      return None, False

