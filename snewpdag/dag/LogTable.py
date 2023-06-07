"""
LogTable - table of logs of integers and factorials
"""
import numpy as np

class LogTable:

  maxn = 1
  logs = np.array([0])
  logfacts = np.array([0])

  def __init__(self, maxn=1000):
    self.ensure(maxn)

  def ensure(self, n):
    nm = np.max(n) # since n could be an array of indices
    if nm >= LogTable.maxn:
      n0 = LogTable.maxn
      n1 = nm + 1
      nvals = np.log(np.arange(n0, n1))
      LogTable.logs = np.append(LogTable.logs, nvals)
      LogTable.logfacts = np.append(LogTable.logfacts, nvals)
      np.cumsum(LogTable.logfacts[n0-1:], out=LogTable.logfacts[n0-1:])
      LogTable.maxn = n1

  def log(self, n):
    self.ensure(n)
    return LogTable.logs[n]

  def logfact(self, n):
    self.ensure(n)
    return LogTable.logfacts[n]

