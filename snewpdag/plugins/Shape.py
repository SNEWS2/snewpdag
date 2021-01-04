"""
Shape: shape comparing methods
also includes the a Bayesian block method
"""
import logging

from snewpdag.dag import Node
import numpy as np

class Shape(Node):
  def __init__(self, nbins, h_low, h_up, scale, dt_0, dt_step, dt_N, polyN, dt_range, **kwargs):
    self.nbins = nbins # number of bins in histograms
    self.h_low = h_low # lower edge of histogram
    self.h_up = h_up # upper edge of histogram
    self.scale = scale # scale factor on the weight for displaced bins
    self.dt_0 = dt_0 # initial dt value (presumably negative)
    self.dt_step = dt_step # dt scan step size
    self.dt_N = dt_N # total number of steps of the dt scan
    self.polyN = ployN # order of the fit polynomial
    self.dt_range = dt_range # metric-dt fit range, fitting +-dt_range around the point of minimum metric
    self.valid = [ False, False ] # flags indicating valid data from sources
    self.h = [ (), () ] # histories from each source
    super().__init__(**kwargs)

    if self.dt_0 > 0:
      logging.error('[{}] Initial dt value positive, will not scan through negative values '.format(self.name, self.dt_0))


  def update(self, data):
    action = data['action']
    source = data['history'][-1]

    # figure out which source updated
    index = self.watch_index(source)
    if index < 0:
      logging.error("[{}] Unrecognized source {}".format(self.name, source))
      return
    if index >= 2:
      logging.error("[{}] Excess source {} detected".format(self.name, source))
      return

    # update the relevant data.
    # Only issue a downstream revocation if the source revocation
    # is new, i.e., the data was valid before.
    for i in range(index+1):
      newrevoke = False
      if action == 'alert':
        self.valid[i] = True
        self.h[i] = data['history']
      elif action == 'revoke':
        newrevoke = self.valid[i]
        self.valid[i] = False
      else:
        logging.error("[{}] Unrecognized action {}".format(self.name, action))
        return

    # do the calculation if we have two valid inputs.
    if self.valid == [ True, True ]:
      mlist = self.metric_list(data[0]['times'], data[1]['times'])
      min_dt = self.minimise(mlist)
      ndata = { 'action': 'alert',
                'history': ( self.h[0], self.h[1] ),
                'dt': min_dt }
      self.notify(ndata)
    elif newrevoke:
      ndata = { 'action': 'revoke',
                'history': ( self.h[0], self.h[1] ) }
      self.notify(ndata)


  def fill_hist(self, values, dt_offset):
    bin_width = (float(self.h_up) - float(self.h_low)) / float(self.nbins)
    hist = [0] * (self.nbins + 2) #add 2 extra bins for underflow and overflow

    for i in range(0, len(values)):
      v = values[i] + dt_offset
      filled = False

      for ii in range(0, self.nbins):
        if v >= (ii * bin_width + self.h_low) and v < ((ii+1) * bin_width + self.h_low):
          hist[ii+1] += 1
          filled = True
          break

      if filled == True:
        continue
      elif v < self.h_low:
        hist[0] += 1
      elif v >= self.h_up:
        hist[len(hist)-1] += 1

    hist = [x/float(len(values)-hist[0]-hist[len(hist)-1]) for x in hist] #normalise excluding flow bins

    return hist


  def remove_flow(hist): #remove the flow bins
    hist.remove(hist[len(hist)-1])
    hist.remove(hist[0])

    return hist


  def diff_hist(self, hist1, hist2):
    h1max = max(hist1) * self.scale
    h2max = max(hist2) * self.scale
    sum_hist = [0] * len(hist1)
    for i in range(len(sum_hist)):
      if hist1[i] != 0 and hist2[i] != 0:
        sum_hist[i] = hist1[i] + hist2[i]
      else:
        sum_hist[i] = h1max + h2max
    diff_hist = [abs(hist2[ii] - hist1[ii]) for ii in range(len(hist1))]    

    metric = 0
    for iii in range(len(diff_hist)):
      metric += sum_hist[iii] * diff_hist[iii]

    return metric


  def metric_list(self, values1, values2):
    mlist = [0] * self.dt_N

    hist2 = self.fill_hist(values2, self.nbins, self.h_low, self.h_up, 0)
    hist2 = self.remove_flow(hist2)
    for i in range(self.dt_N):
      hist1 = self.fill_hist(values1, self.nbins, self.h_low, self.h_up, self.dt_0 + i*self.dt_step)
      hist1 = self.remove_flow(hist1)
      metric = self.diff_hist(hist1, hist2, self.scale)
      mlist[i] = metric

    return mlist


  def minimise(self, mlist):
    dt_list = [(self.dt_0 + i*self.dt_step) for i in range(self.dt_N)]

    #setting fit range
    i_dt_range = int(self.dt_range / self.dt_step)
    i_min_metric = np.argmin(mlist)
    i_low = 0
    i_up = self.dt_N - 1
    if (i_min_metric - i_dt_range) > 0:
      i_low = i_min_metric - i_dt_range
    if (i_min_metric + i_dt_range) < (self.dt_N - 1):
      i_up = i_min_metric + i_dt_range
    coeff = np.polyfit(dt_list[i_low:i_up], mlist[i_low:i_up], self.polyN) #polynomial fit, coeff[0]*x^polyN + coeff[1]*x^(polyN-1) + ...

    min_dt = 0
    func_prev = 0
    for ii in range(len(dt_list)):
      func = 0
      for iii in range(self.polyN+1):
        func += coeff[iii] * pow(self.dt_0 + ii*self.dt_step, self.polyN-iii)

      if ii == 0:
        func_prev = func
        continue
      else:
        if func * func_prev > 0:
          func_prev = func
          continue
        if func * func_prev <= 0:
          min_dt = self.dt_0 + ii*self.dt_step
          break

    return min_dt
