"""
Shape: shape comparing methods
also includes the Bayesian block method
"""
import logging
import math
from snewpdag.dag import Node
from snewpdag.plugins import ShapeHist
from snewpdag.plugins import ShapeHistFunctions as SHF
import numpy as np


class ShapeComparison(Node):
  def __init__(self, shapehist, scale, dt0, dt_step, dt_N, polyN, fit_range, **kwargs):
    self.h_bins = shapehist.h_bins # number of bins in histograms
    self.h_low = shapehist.h_low # lower edge of histogram
    self.h_up = shapehist.h_up # upper edge of histogram
    self.scale = scale # scale factor on the weight for displaced bins
    self.dt0 = dt0 # initial dt value for scan (presumably negative)
    self.dt_step = dt_step # dt scan step size
    self.dt_N = dt_N # total number of steps of the dt scan
    self.polyN = polyN # order of the fit polynomial
    self.fit_range = fit_range # metric-dt fit range, fitting +-dt_range around the point of minimum metric
    self.valid = [ False, False ] # flags indicating valid data from sources
    self.h = [ (), () ] # histories from each source
    self.history_data = []
    super().__init__(**kwargs)

    if self.dt0 > 0:
      logging.error('[{}] Initial dt value positive, will not scan through negative values '.format(self.name, self.dt0))


  def update(self, data):
    action = data['action']

    index = len(self.history_data)

    # update the relevant data.
    # Only issue a downstream revocation if the source revocation
    # is new, i.e., the data was valid before.
    newrevoke = False
    if action == 'alert':
      self.valid[index] = True
      self.h[index] = data['name']
      self.history_data.append(data['times'])
    elif action == 'revoke' :
      newrevoke = self.valid[index]
      self.valid[index] = False
    else:
      logging.error("[{}] Unrecognized action {}".format(self.name, action))
      return

    # do the calculation if we have two valid inputs.
    if self.valid == [ True, True ]:
      mlist = self.metric_list(data['times'], self.history_data[index-1])
      min_dt = SHF.minimise(mlist, self.dt0, self.dt_step, self.dt_N, self.polyN, self.fit_range)
      print("dt = " + str(min_dt))
      self.notify('alert', (self.h[0], self.h[1]), {'dt': min_dt})
    elif newrevoke:
      self.notify('revoke', (self.h[0], self.h[1]), {})


  def metric_list(self, values1, values2):
    mlist = [0.0] * self.dt_N

    hist2 = ShapeHist.ShapeHist(self.h_bins, self.h_low, self.h_up).fill_hist(values2, 0.0)
    hist2 = SHF.remove_flow(hist2)
    for i in range(self.dt_N):
      hist1 = ShapeHist.ShapeHist(self.h_bins, self.h_low, self.h_up).fill_hist(values1, self.dt0 + i*self.dt_step)
      hist1 = SHF.remove_flow(hist1)
      metric = SHF.diff_hist(hist1, hist2, self.scale)

      mlist[i] = metric

    return mlist
