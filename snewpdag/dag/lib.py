"""
lib
"""
import logging
import numpy as np

def normalize_time(a):
  """
  Normalize time array.
  """
  if np.shape(a)[-1] < 2:
    logging.error("input array has wrong shape {}".format(np.shape(a)))
    return None
  g = 1000000000
  t = np.array(a, copy=True)
  np.add(t[...,0], np.floor_divide(t[...,1], g), out=t[...,0])
  np.remainder(t[...,1], g, out=t[...,1])
  return t

