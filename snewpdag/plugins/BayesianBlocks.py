"""
Bayes: Bayesian block method.  It's now set to always run in hybrid mode.  To run a pure Bayesian block, set division to be lower than h_low
"""
import logging
import math
from snewpdag.dag import Node
from snewpdag.plugins import ShapeHistFunctions as SHF
import numpy as np


class BayesianBlocks(Node):
  def __init__(self, h_bins, h_low, h_up, shape, gamma, division, **kwargs):
    self.h_bins = h_bins # number of bins in histograms
    self.h_low = h_low # lower edge of histogram
    self.h_up = h_up # upper edge of histogram
    self.scale = shape.scale # scale factor on the weight for displaced bins
    self.dt0 = shape.dt0 # initial dt value for scan (presumably negative)
    self.dt_step = shape.dt_step # dt scan step size
    self.dt_N = shape.dt_N # total number of steps of the dt scan
    self.polyN = shape.polyN # order of the fit polynomial
    self.fit_range = shape.fit_range # metric-dt fit range, fitting +-dt_range around the point of minimum metric
    self.gamma = gamma # prior probability used in the Bayesian block method, larger gamma means finer bins
    self.division = division # division between uniform bins and Bayesian blocks
    self.valid = [ False, False ] # flags indicating valid data from sources
    self.h = [ (), () ] # histories from each source
    self.history_data = []
    self.hybrid_bin_value = []
    super().__init__(**kwargs)

    if self.dt0 > 0:
      logging.error('[{}] Initial dt value positive, will not scan through negative values '.format(self.name, self.dt0))

    if self.division < self.h_low:
      self.division = self.h_low


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
    mlist = [0] * self.dt_N

    block2 = self.bayesian_block(values2)
    hist2 = self.block_hist(block2[0], block2[1], 0)
    for i in range(self.dt_N):
      block1 = self.bayesian_block(values1)
      hist1 = self.block_hist(block1[0], block1[1], self.dt0 + i*self.dt_step)
      metric = SHF.diff_hist(hist1, hist2, self.scale)
      mlist[i] = metric

    return mlist


  def bayesian_block(self, values):
    log_prior = math.log(self.gamma)

    svalues = []
    for iv in range(len(values)):
      if float(values[iv]) >= self.h_low and float(values[iv]) < self.h_up:
        self.hybrid_bin_value.append(float(values[iv]))           
        if float(values[iv]) > self.division:
          svalues.append(float(values[iv]))
      else:
        values.remove(values[iv])
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

    best_content = [x/float(len(values)) for x in best_content]

    bayes_block.append(best_edge)
    bayes_block.append(best_content)

    return bayes_block


  def block_hist(self, block_edge, block_content, dt_offset):
    bin_width = (float(self.h_up) - float(self.h_low)) / float(self.h_bins)
    hist = [0] * (self.h_bins)

    block_width = [block_edge[ie] - block_edge[ie-1] for ie in range(len(block_edge)) if ie > 0]

    edge_index = 0
    for i in range(self.h_bins): #fill in the bins of the histogram
      bin_edge = self.h_low + (i+1) * bin_width #upper edge of the bin

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
          hist[i] += (block_content[-1]/block_width[-1]) * ( (block_edge[-1]+dt_offset) - bin_edge + bin_width)
          break
        else: #if the bin includes full blocks
          ib = 1 #number of block edges included in the bin
          while bin_edge - bin_width < block_edge[-1-ib]+dt_offset:
            ib += 1

          hist[i] += (block_content[-ib]/block_width[-ib]) * ( (block_edge[-ib]+dt_offset) - bin_edge + bin_width)
          for iib in range(ib-1):
            hist[i] += (block_content[-1-iib]/block_width[-1-iib]) * (block_edge[-1-iib] - block_edge[-2-iib])
          break

      if block_edge[edge_index]+dt_offset >= bin_edge:
        if edge_index == 1: #if the bin is completely or partially in the first block
          if bin_edge - bin_width < block_edge[edge_index-1]+dt_offset: #if the bin is partially in the first block
            hist[i] += (block_content[edge_index-1]/block_width[edge_index-1]) * (bin_edge - (block_edge[edge_index-1]+dt_offset) )
            continue
          else: #if the bin is completely in the first block
            hist[i] += (block_content[edge_index-1]/block_width[edge_index-1]) * bin_width
            continue
        elif bin_edge - bin_width >= block_edge[edge_index-1]+dt_offset: #if the bin is completely within one single block
          hist[i] += (block_content[edge_index-1]/block_width[edge_index-1]) * bin_width
          continue
        else: #if the bin is only partially in a block or even contains several blocks
          ib = 1 #number of block edges included in the bin
          while bin_edge - bin_width < block_edge[edge_index-1-ib]+dt_offset:
            ib += 1

          hist[i] += (block_content[edge_index-1]/block_width[edge_index-1]) * (bin_edge - (block_edge[edge_index-1]+dt_offset))
          for iib in range(ib-1):
            hist[i] += (block_content[edge_index-2-iib]/block_width[edge_index-2-iib]) * (block_edge[edge_index-1-iib] - block_edge[edge_index-2-iib])
          hist[i] += (block_content[edge_index-1-ib]/block_width[edge_index-1-ib]) * ( (block_edge[edge_index-ib]+dt_offset) - bin_edge + bin_width)
          continue

    for i in range(self.h_bins):
      bin_up_edge = self.h_low + (i+1) * bin_width #upper edge of the bin
      bin_low_edge = self.h_low + i * bin_width #lower edge of the bin

      for ii in range(len(self.hybrid_bin_value)):
        if self.hybrid_bin_value[ii]+dt_offset > bin_low_edge and self.hybrid_bin_value[ii]+dt_offset <= bin_up_edge and self.hybrid_bin_value[ii] <= self.division:
          hist[i] += 1/float(len(self.hybrid_bin_value))
    self.hybrid_bin_value.clear()

    return hist



