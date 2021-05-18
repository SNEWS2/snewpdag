import math
import numpy as np


def fill_hist(h_bins, h_low, h_up, values, dt_offset):
  bin_width = (float(h_up) - float(h_low)) / float(h_bins)
  hist = [0.0] * (h_bins + 2) #add 2 extra bins for underflow and overflow

  for i in range(0, len(values)):
    v = values[i] + dt_offset
    filled = False

    for ii in range(0, h_bins):
      if v >= (ii * bin_width + h_low) and v < ((ii+1) * bin_width + h_low):
        hist[ii+1] += 1
        filled = True
        break

    if filled == True:
      continue
    elif v < h_low:
      hist[0] += 1
    elif v >= h_up:
      hist[len(hist)-1] += 1

  hist = [float(x)/float(float(len(values))-hist[0]-hist[-1]) for x in hist] #normalise excluding flow bins

  return hist


def remove_flow(hist): #remove the flow bins
  hist.remove(hist[-1])
  hist.remove(hist[0])

  return hist


def diff_hist(hist1, hist2, scale):
  if len(hist1) != len(hist2):
    print("histograms with different number of bins cannot be merged!")
    exit()

  h1max = max(hist1) * scale
  h2max = max(hist2) * scale
  sum_hist = [0.0] * len(hist1)
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


def minimise(mlist, dt0, dt_step, dt_N, polyN, fit_range):
  dt_list = [(dt0 + i*dt_step) for i in range(dt_N)]

  #setting fit range
  i_fit_range = int(fit_range / dt_step) + 1
  i_min_metric = np.argmin(mlist)
  i_low = 0
  i_up = dt_N - 1
  if (i_min_metric - i_fit_range) > 0:
    i_low = i_min_metric - i_fit_range
  if (i_min_metric + i_fit_range) < (dt_N - 1):
    i_up = i_min_metric + i_fit_range
  coeff = np.polyfit(dt_list[i_low:i_up], mlist[i_low:i_up], polyN) #polynomial fit, coeff[0]*x^polyN + coeff[1]*x^(polyN-1) + ...

  min_dt = 0
  func_prev = 0
  for ii in range(len(dt_list)):
    func = 0
    for iii in range(polyN):
      func += coeff[iii] * (polyN - iii) * pow(dt_list[ii], polyN-1-iii)

    if ii == 0:
      func_prev = func
      continue
    if func * func_prev <= 0:
      min_dt = (dt_list[ii] + dt_list[ii-1])/2.0
      break
    func_prev = func

  return min_dt
