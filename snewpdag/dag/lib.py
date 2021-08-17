"""
DAG library routines
"""
import logging
import numpy as np

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
  g = 1000000000
  t = np.array(a, copy=True)
  np.add(t[...,0], np.floor_divide(t[...,1], g), out=t[...,0])
  np.remainder(t[...,1], g, out=t[...,1])
  return t

def normalize_time_difference(a):
  """
  Normalize time difference array.
  A time difference will have the form (s, ns), where both are integers.
  In this case, s and ns have the same sign or zero.
  """
  t = normalize_time(a)
  g = 1000000000
  mask = np.logical_and(np.less(t[...,0], 0), np.not_equal(t[...,1], 0))
  np.add(t[...,0], 1, out=t[...,0], where=mask)
  np.subtract(t[...,1], g, out=t[...,1], where=mask)
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
  g = 1000000000
  dt = np.subtract(a, b)
  return normalize_time_difference(dt)

