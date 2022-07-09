"""
DAG library routines
"""
import logging
import numpy as np

ns_per_second = 1000000000

def time_tuple_from_float(x):
  """
  Turn floats (seconds) into time tuples of (s,ns).
  """
  s = np.floor(x)
  ns = (x - s) * ns_per_second
  return np.stack((s,ns), axis=-1)

def time_tuple_from_offset(ns):
  """
  Turn offsets (ns) into time tuples of (s,ns).
  """
  if np.isscalar(ns):
    return normalize_time((0, ns))
  else:
    s = np.zeros(len(ns))
    return normalize_time(np.stack((s, ns), axis=-1))

def offset_from_time_tuple(tt):
  d = np.array(tt)
  s = np.multiply(d[...,0], ns_per_second, dtype=np.int64)
  t = np.add(s, d[...,1], dtype=np.int64)
  return t

def normalize_time(a):
  """
  Normalize time array.
  The simplest time array is a tuple (s,ns), where both are integers
  and ns is between 0 and 999999999 (1e9 - 1).

  This routine will take an array of almost arbitrary shape,
  the only requirement being that the last dimension is at least 2 wide,
  in which case [0] is s and [1] is ns.  

  It will return an array of the same shape, but with the time tuples
  normalized, i.e., ns in the range specified above, and s adjusted
  accordingly.
  """
  if np.shape(a)[-1] < 2:
    logging.error("input array has wrong shape {}".format(np.shape(a)))
    return None
  t = np.array(a, copy=True)
  np.add(t[...,0], np.floor_divide(t[...,1], ns_per_second), out=t[...,0])
  np.remainder(t[...,1], ns_per_second, out=t[...,1])
  return t

def normalize_time_difference(a):
  """
  Normalize time difference array.
  A time difference will have the form (s, ns), where both are integers.
  In this case, s and ns have the same sign or zero.
  """
  t = normalize_time(a)
  mask = np.logical_and(np.less(t[...,0], 0), np.not_equal(t[...,1], 0))
  np.add(t[...,0], 1, out=t[...,0], where=mask)
  np.subtract(t[...,1], ns_per_second, out=t[...,1], where=mask)
  return t

def subtract_time(a, b):
  """
  Subtract time arrays and returned normalized time differences.
  """
  if np.shape(a)[-1] < 2:
    logging.error("input array has wrong shape {}".format(np.shape(a)))
    return None
  if np.shape(b)[-1] < 2:
    logging.error("input array has wrong shape {}".format(np.shape(b)))
    return None
  dt = np.subtract(a, b)
  return normalize_time_difference(dt)

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
      else:
        return None, False
    return d, True
  else:
    if fields in data:
      return data[fields], True
    else:
      return None, False

