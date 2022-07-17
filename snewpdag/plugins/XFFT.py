"""
XFFT - calculate dt with cross-correlation using FFT's

Arguments:
  det1:  detector id for first detector in watch_list
  det2:  detector id for second detector in watch_list
  duration:  time window for FFT in seconds
  nbins:  number of time bins
  in_field:  input field name for TimeHist or TimeSeries

Input data:
  (in_field):  TimeHist or TimeSeries

For now, we'll assume they're TimeSeries objects with durations
and the same start time.
Later:
* for TimeHist objects, need to align their times in case they have
  different starting times.
* for TimeSeries objects, align times if they have different start times.

Output data:
  dts/dt: time tuple of (s,ns) of t1-t2
      ft1: FT of det1 data (complex ndarray)
      ft2: FT of det2 data
      ftxc: FT of cross-correlation (ft1 * conj(fg2))
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.values import TimeSeries
from snewpdag.dag.lib import ns_per_second

class XFFT(Node):
  def __init__(self, det1, det2, nbins, duration, in_field, **kwargs):
    self.det1 = det1
    self.det2 = det2
    self.nbins = nbins
    self.duration = duration
    self.in_field = in_field
    self.data1 = None
    self.data2 = None
    super().__init__(**kwargs)

  def ffts(self, dt, data1, data2):
    """
    calculate FT of cross-correlation.
    Assume data1 and data2 are TimeSeries objects with same starting time.
    """
    th1, bin_edges = np.histogram(data1.times / ns_per_second, bins=self.nbins,
                                  range=(0, self.duration))
    th2, bin_edges = np.histogram((data2.times / ns_per_second) - dt, bins=self.nbins,
                                  range=(0, self.duration))

    logging.debug('{}: histograms')
    for i in range(10):
      logging.debug('  {}: {} {}'.format(i, th1[i], th2[i]))

    self.ft1 = np.fft.rfft(th1)
    self.ft2 = np.fft.rfft(th2)
    self.ftxc = self.ft1 * np.conjugate(self.ft2)

  def alert(self, data):
    # cache data
    index = self.last_watch_index()
    if index == 0:
      self.data1 = data[self.in_field]
    elif index == 1:
      self.data2 = data[self.in_field]
    else:
      logging.error('{}: invalid watch index {}'.format(self.name, index))
      return False

    # test if have enough data
    if self.data1 == None or self.data2 == None:
      return False

    # have time data from both sources.
    # Now try a dt hypothesis.
    dt = 0.01
    self.ffts(dt, self.data1, self.data2)

    logging.debug('{}: components'.format(self.name))
    for i in range(10):
      logging.debug('  {}: ({}) ({}) ({})'.format(i,
                    self.ft1[i], self.ft1[i], self.ftxc[i]))

    # stuff back into the payload
    dts = {
            'dt': dt,
            'ft1': self.ft1,
            'ft2': self.ft2,
            'ftxc': self.ftxc,
          }
    if 'dts' not in data:
      data['dts'] = {}
    data['dts'][(self.det1, self.det2)] = dts
    return data

  def revoke(self, data):
    index = self.last_watch_index()
    if index == 0:
      self.data1 = None
    elif index == 1:
      self.data2 = None
    else:
      logging.error('{}: reset invalid watch index {}'.format(self.name, index))
    return False

  def reset(self, data):
    self.data1 = None
    self.data2 = None
    return False

