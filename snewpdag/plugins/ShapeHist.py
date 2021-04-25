import logging
import math
import numpy as np


class ShapeHist():
  def __init__(self, h_bins, h_low, h_up):
    self.h_bins = h_bins
    self.h_low = h_low
    self.h_up = h_up


  def fill_hist(self, values, dt_offset):
    bin_width = (float(self.h_up) - float(self.h_low)) / float(self.h_bins)
    hist = [0.0] * (self.h_bins + 2) #add 2 extra bins for underflow and overflow

    for i in range(0, len(values)):
      v = values[i] + dt_offset
      filled = False

      for ii in range(0, self.h_bins):
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

    hist = [float(x)/float(float(len(values))-hist[0]-hist[-1]) for x in hist] #normalise excluding flow bins

    return hist
