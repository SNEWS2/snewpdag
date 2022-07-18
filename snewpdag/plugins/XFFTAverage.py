"""
XFFTAverage - analysis plugin for XFFT trials

Arguments:
  in_field:  input field name for FT to analyze
  out_avg_field:  output field for phase averages
  out_ft_base (optional):  output field base
  nfreq (optional):  number of frequency components for which to make Hist1D's

Input data:
  (in_field):  array of complex frequency component amplitudes

Output data:
  (out_avg_field):  Hist1D of average phases for all frequency components
  (out_ft_base)_mag[]:  Hist1D's of magnitudes
  (out_ft_base)_phi[]:  Hist1D's of angles
"""
import logging
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field
from snewpdag.values import Hist1D

class XFFTAverage(Node):
  def __init__(self, in_field, out_avg_field, **kwargs):
    self.in_field = in_field
    self.out_avg_field = out_avg_field
    self.nfreq = kwargs.pop('nfreq', 0)
    self.out_ft_base = kwargs.pop('out_ft_base', 'fft')
    self.count = 0 # number of trials accumulated
    if self.nfreq > 0:
      self.hmag = [ Hist1D(100, 0.0, 100.0) for i in range(self.nfreq) ]
      self.hphi = [ Hist1D(320, -3.2, 3.2) for i in range(self.nfreq) ]
    super().__init__(**kwargs)

  def alert(self, data):
    ft, flag = fetch_field(data, self.in_field)
    if flag:
      if self.count == 0:
        self.sy = np.zeros(len(ft)) # sums in each bin
        self.ssy = np.zeros(len(ft)) # sums of squares in each bin
      phi = np.angle(ft)
      self.sy += phi
      self.ssy += phi * phi
      if self.nfreq > 0:
        mag = np.abs(ft)
        for i in range(self.nfreq):
          self.hmag[i].fill(mag[i])
          self.hphi[i].fill(phi[i])
      self.count += 1
    return False

  def report(self, data):
    h = Hist1D(len(self.sy), 0, len(self.sy))
    h.bins = self.sy / self.count
    h.errs = np.sqrt(self.ssy - self.sy * self.sy) / self.count
    data[self.out_avg_field] = h
    if self.nfreq > 0:
      data['{}_mag'.format(self.out_ft_base)] = [ \
          self.hmag[i] for i in range(self.nfreq) ]
      data['{}_phi'.format(self.out_ft_base)] = [ \
          self.hphi[i] for i in range(self.nfreq) ]
    return data

