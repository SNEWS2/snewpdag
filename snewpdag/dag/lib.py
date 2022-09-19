"""
DAG library routines
"""
import logging
import numbers
import numpy as np
from astropy.time import Time
from astropy import units as u

ns_per_second = 1000000000

def t2ns(t, unit=None):
  """
  Turns a timestamp into ns timestamp (dtype np.int64) from Unix epoch,
  trying to preserve ns precision.

  If x is dimensionless, assume it's in seconds.
  Use the unit argument to override the units of x.

  Return value is numeric, rather than a Quantity (which is always float64).
  """
  x = t.value if hasattr(t, 'value') else t # strip off units
  if unit == u.ns:
    return np.array(x, dtype=np.int64)
  else:
    if unit == None:
      if hasattr(t, 'unit'):
        uu = t.unit
      else:
        uu = u.s
    else:
      uu = unit
      if uu == u.ns:
        return np.array(x, dtype=np.int64)
    s = np.floor(x).astype(np.int64)
    if uu > u.ns: # for longer units than ns (normal)
      g = np.rint(uu.to(u.ns)).astype(np.int64) # multiplier
      # for some reason, u.s.to(u.ns) gives 999999999.999 in astropy,
      # though other conversions seem to be fine.
      ns = ((x - s) * g).astype(np.int64)
      #logging.info('t2ns: s={}, ns={}, g={}'.format(s,ns,g))
      return s * g + ns
    else:
      g = np.array(u.ns.to(uu)).astype(np.int64) # divider
      ns = (s / g).astype(np.int64)
      return ns

def string2ns(s):
  t = Time(s)
  ts = t.to_value('unix', 'long') # can return a float
  return t2ns(ts)

def field2ns(s, unit=None):
  """
  s is a single value:
    Quantity - assumed to be time-like, since Unix epoch
    float - time in seconds in Unix epoch
    (s, ns) - Unix epoch
    string - UTC time string
    (string, ns) - UTC time string for seconds, ns field
      unfortunately the last one doesn't seem to be supported with
      csv configuration files. Something to do with the parser?
  unit can specify/override the unit of s if it's already a Quantity.
  """
  if isinstance(s, numbers.Number):
    return t2ns(s, unit=unit)
  elif isinstance(s, str):
    return string2ns(s)
  elif isinstance(s, u.Quantity):
    return t2ns(value, unit=unit) # convert to seconds first, then to ns
  elif isinstance(s, (list, tuple, np.ndarray)):
    if isinstance(s, np.ndarray): # single numbers in an ndarray
      if s.shape == ():
        return t2ns(s, unit=unit)
      elif s.shape == (1,):
        return t2ns(s[0], unit=unit)
    if isinstance(s[1], numbers.Number): # old (s,ns)
      if isinstance(s[0], numbers.Number):
        return np.int64(s[0]) * ns_per_second + np.int64(s[1])
      elif isinstance(s[0], str):
        return string2ns(s[0]) + np.int64(s[1])

# deprecated
def time_tuple_from_float(x):
  """
  Turn floats (seconds) into time tuples of (s,ns).
  """
  s = np.floor(x).astype(np.int64)
  ns = ((x - s) * ns_per_second).astype(np.int64)
  return np.stack((s,ns), axis=-1)

# deprecated
def time_tuple_from_offset(ns):
  """
  Turn offsets (ns) into time tuples of (s,ns).
  """
  if np.isscalar(ns):
    return normalize_time((0, ns))
  else:
    s = np.zeros(len(ns))
    return normalize_time(np.stack((s, ns), axis=-1))

# deprecated
def time_tuple_from_string(s):
  t = Time(s)
  ts = t.to_value('unix', 'long')
  ti = int(ts)
  tf = ts - ti
  return (ti, int(tf * ns_per_second))

# deprecated
def time_tuple_from_field(s):
  """
  float - time in seconds in Unix epoch
  (n, ns) - Unix epoch
  string - UTC time string
  (string, ns) - UTC time string for seconds, nanoseconds field
    unfortunately the last one doesn't seem to be supported with
    csv configuration files. Something to do with the parser?
  """
  if isinstance(s, numbers.Number):
    return time_tuple_from_float(s)
  elif isinstance(s, str):
    return time_tuple_from_string(s)
  elif isinstance(s, (list, tuple, np.ndarray)):
    if isinstance(s[1], numbers.Number):
      if isinstance(s[0], numbers.Number):
        return np.array(s[:2])
      elif isinstance(s[0], str):
        t0 = time_tuple_from_string(s[0])
        t0[1] += s[1]
        return normalize_time(t0)
  return None

# deprecated
def offset_from_time_tuple(tt):
  d = np.array(tt)
  s = np.multiply(d[...,0], ns_per_second, dtype=np.int64)
  t = np.add(s, d[...,1], dtype=np.int64)
  return t

# deprecated
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

# deprecated
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

# deprecated
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

