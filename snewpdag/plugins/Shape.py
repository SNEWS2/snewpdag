"""
Shape: shape comparing methods
also includes the Bayesian block method
"""
import logging
import math
from snewpdag.dag import Node
import numpy as np

class Shape(Node):
  def __init__(self, nbins, h_low, h_up, scale, dt_0, dt_step, dt_N, polyN, dt_range, mode, gamma, **kwargs):
    self.nbins = nbins # number of bins in histograms
    self.h_low = h_low # lower edge of histogram
    self.h_up = h_up # upper edge of histogram
    self.scale = scale # scale factor on the weight for displaced bins
    self.dt_0 = dt_0 # initial dt value for scan (presumably negative)
    self.dt_step = dt_step # dt scan step size
    self.dt_N = dt_N # total number of steps of the dt scan
    self.polyN = polyN # order of the fit polynomial
    self.dt_range = dt_range # metric-dt fit range, fitting +-dt_range around the point of minimum metric
    self.mode = mode # shape matching mode, 0) uniform bins 1) Bayesian blocks 2) bins + blocks
    self.gamma = gamma # prior probability used in the Bayesian block method, larger gamma means finer bins
    self.valid = [ False, False ] # flags indicating valid data from sources
    self.h = [ (), () ] # histories from each source
    self.history_data = []
    super().__init__(**kwargs)

    if self.dt_0 > 0:
      logging.error('[{}] Initial dt value positive, will not scan through negative values '.format(self.name, self.dt_0))


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
      min_dt = self.minimise(mlist)
      print("dt = " + str(min_dt))
      self.notify('alert', (self.h[0], self.h[1]), {'dt': min_dt})
    elif newrevoke:
      self.notify('revoke', (self.h[0], self.h[1]), {})


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

    hist = [x/float(len(values)-hist[0]-hist[-1]) for x in hist] #normalise excluding flow bins

    return hist


  def remove_flow(self, hist): #remove the flow bins
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

    if self.mode == 0:
      hist2 = self.fill_hist(values2, 0)
      hist2 = self.remove_flow(hist2)
      for i in range(self.dt_N):
        hist1 = self.fill_hist(values1, self.dt_0 + i*self.dt_step)
        hist1 = self.remove_flow(hist1)
        metric = self.diff_hist(hist1, hist2)
        mlist[i] = metric
    if self.mode == 1:
      block2 = self.bayesian_block(values2)
      hist2 = self.block_hist(block2[0], block2[1], 0)
      for i in range(self.dt_N):
        block1 = self.bayesian_block(values1)
        hist1 = self.block_hist(block1[0], block1[1], self.dt_0 + i*self.dt_step)
        metric = self.diff_hist(hist1, hist2)
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


  def bayesian_block(self, values):
    log_prior = math.log(self.gamma)

    svalues = []
    for iv in range(len(values)):
      if float(values[iv]) >= self.h_low and float(values[iv]) < self.h_up:
        svalues.append(float(values[iv]))
    svalues.sort()

    edge = [(svalues[i] + svalues[i-1])/2 for i in range(len(svalues)) if i > 0]
    edge.insert(0, 1.5*svalues[0] - 0.5*svalues[1]) #lower edge of the first cell
    edge.append(1.5*svalues[-1] - 0.5*svalues[-2]) #upper edge of the last cell

    width = [(edge[ii] - edge[ii-1]) for ii in range(len(edge)) if ii > 0]

    best = [] #best[N] = the likelihood of the best combination when there are N+1 data points
    best_count = [] #best_count[N] = the number of data points in the last block when there are N+1 data points

    for n in range(1, len(svalues) + 1): #start from 1 data point and add one point a time
      last_n = n #number of data points in the last block 

      if n == 1: #for only one data point the best partition is certainly one block
        block_width = width[0]
        max_like = 1 * (math.log(1/block_width)) + log_prior
        best.append(max_like)
        best_count.append(1)
      else:
        block_width = 0
        for nn in range(0, last_n):
          block_width += width[nn]
        max_like = last_n * (math.log(last_n/block_width)) + log_prior
        best_n = last_n
        last_n -= 1
        while last_n > 0:
          block_width = 0
          for nn in range(0, last_n):
            block_width += width[n-1-nn]
          like = last_n * (math.log(last_n/block_width)) #likelihood for the last block
          like += best[n-last_n-1] #likelihood of the best partition for the data points not in the last block
          like += log_prior #suppresion prior for creating a new block
          if like > max_like:
            max_like = like
            best_n = last_n
          last_n -= 1
        best.append(max_like)
        best_count.append(best_n)

    best_edge = []
    best_content = []
    bayes_block = []

    best_edge.append(edge[-1])
    dataN = len(svalues)
    edge_index = -1
    while dataN > 0:
      best_content.append(best_count[dataN-1])
      edge_index -= best_count[dataN-1]
      best_edge.append(edge[edge_index])
      dataN -= best_count[dataN-1]

    best_content.reverse()
    best_edge.reverse()

    best_content = [x/(float(len(svalues))) for x in best_content] #normalising the blocks

    bayes_block.append(best_edge)
    bayes_block.append(best_content)

    return bayes_block


  def block_hist(self, block_edge, block_content, dt_offset):
    bin_width = (float(self.h_up) - float(self.h_low)) / float(self.nbins)
    hist = [0] * (self.nbins)

    block_width = [block_edge[ie] - block_edge[ie-1] for ie in range(len(block_edge)) if ie > 0]

    edge_index = 0
    for i in range(self.nbins): #fill in the bins of the histogram
      bin_edge = self.h_low + i * bin_width #upper edge of the bin

      if edge_index == 0 and bin_edge <= block_edge[edge_index]+dt_offset: #if the bin is below the lower end of the blocks
        hist[i] = 0
        continue

      reach_end = False
      while block_edge[edge_index]+dt_offset < bin_edge: #loop until there's a block whose upper edge covers the bin
        edge_index += 1

        if edge_index == len(block_edge): #flag when the upper bin edge exceeds the upper end of the blocks
          reach_end = True
          break

      if reach_end == True: #when the upper bin edge exceeds the upper end of the blocks
        if bin_edge - bin_width >= block_edge[-2]+dt_offset: #if the bin doesn't include any full blocks
          hist[i] = (block_content[-1]/block_width[-1]) * ( (block_edge[-1]+dt_offset) - bin_edge + bin_width)
          break
        else: #if the bin includes full blocks
          ib = 1 #number of block edges included in the bin
          while bin_edge - bin_width < block_edge[-1-ib]+dt_offset:
            ib += 1

          hist[i] = (block_content[-ib]/block_width[-ib]) * ( (block_edge[-ib]+dt_offset) - bin_edge + bin_width)
          for iib in range(ib-1):
            hist[i] += (block_content[-1-iib]/block_width[-1-iib]) * (block_edge[-1-iib] - block_edge[-2-iib])
          break

      if block_edge[edge_index]+dt_offset >= bin_edge:
        if edge_index == 1: #if the bin is completely or partially in the first block
          if bin_edge - bin_width < block_edge[edge_index-1]+dt_offset: #if the bin is partially in the first block
            hist[i] = (block_content[edge_index-1]/block_width[edge_index-1]) * (bin_edge - (block_edge[edge_index-1]+dt_offset) )
            continue
          else: #if the bin is completely in the first block
            hist[i] = (block_content[edge_index-1]/block_width[edge_index-1]) * bin_width
            continue
        elif bin_edge - bin_width >= block_edge[edge_index-1]+dt_offset: #if the bin is completely within one single block
          hist[i] = (block_content[edge_index-1]/block_width[edge_index-1]) * bin_width
          continue
        else: #if the bin is only partially in a block or even contains several blocks
          ib = 1 #number of block edges included in the bin
          while bin_edge - bin_width < block_edge[edge_index-1-ib]+dt_offset:
            ib += 1

          hist[i] = (block_content[edge_index-1]/block_width[edge_index-1]) * (bin_edge - (block_edge[edge_index-1]+dt_offset))
          for iib in range(ib-1):
            hist[i] += (block_content[edge_index-2-iib]/block_width[edge_index-2-iib]) * (block_edge[edge_index-1-iib] - block_edge[edge_index-2-iib])
          hist[i] += (block_content[edge_index-1-ib]/block_width[edge_index-1-ib]) * ( (block_edge[edge_index-ib]+dt_offset) - bin_edge + bin_width)
          continue

    return hist



