"""
1D Histogram renderer

Configuration options:
  title:  histogram title (top of plot)
  xlabel:  x axis label
  ylabel:  y axis label
  filename:  output filename, with fields
             {0} renderer name
             {1} count index, starting from 0
             {2} id from update data (default 0 if no such field)
  true_dist: true distance if needed (used for Gaussian fitting comparisons)

Might be nice to allow options to be configured here as well.

Input data:
  action - only respond to 'report'
  id - burst id
  xlow
  xhigh
  bins - uniform bin contents
  in_field - optional, dictionary name of input
             (otherwise look in payload dictionary itself)
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
import matplotlib.mlab as mlab

from snewpdag.dag import Node

class Histogram1D(Node):
  def __init__(self, title, xlabel, ylabel, filename, **kwargs):
    self.title = title
    self.xlabel = xlabel
    self.ylabel = ylabel
    self.filename = filename # include pattern to include index
    self.in_field = kwargs.pop('in_field', None)
    self.mode = kwargs.pop('mode', None)
    self.count = 0 # number of histograms made
    self.true_dist = kwargs.pop('true_dist', None)
    super().__init__(**kwargs)

  def render(self, burst_id, xlo, xhi, bins):
    n = len(bins)
    step = (xhi - xlo) / n
    x = np.arange(xlo, xhi, step)

    fig, ax = plt.subplots()
    ax.bar(x, bins, width=step, align='edge')
    #ax.plot(x, bins)
    ax.set_xlabel(self.xlabel)
    ax.set_ylabel(self.ylabel)
    ax.set_title('{0} (burst {1} count {2})'.format(
                 self.title, burst_id, self.count))
    fig.tight_layout()

    fname = self.filename.format(self.name, self.count, burst_id)
    plt.savefig(fname)
    self.count += 1

  def render_Gaussian(self, burst_id, xlo, xhi, bins, mean, std, exp_mean, exp_std):
    n = len(bins)
    step = (xhi - xlo) / n
    x = np.arange(xlo, xhi, step)
    x_Gauss = np.linspace(mean - 3*std, mean + 3*std, 100)
    x_exp_Gauss = np.linspace(exp_mean - 3*exp_std, exp_mean + 3*exp_std, 100)
    
    fig, ax = plt.subplots()
    ax.bar(x, bins, width=step, align='edge')
    ax.set_xlabel(self.xlabel)
    ax.set_ylabel(self.ylabel)
    ax.set_title('{} (burst {} count {})\nGaussian Fit: mean = {:.2f}, std = {:.2f}'
                .format(self.title, burst_id, self.count, mean, std))
    fig.tight_layout()

    scale = sum(bins) * step
    plt.plot(x_Gauss, norm.pdf(x_Gauss, mean, std) * scale, linewidth=2, color='r', label='Gaussian Fit')
    plt.plot(x_exp_Gauss, norm.pdf(x_exp_Gauss, exp_mean, exp_std) * scale, linewidth=2, color='g', label='Expected Distrib')
    plt.legend()

    fname = self.filename.format(self.name, self.count, burst_id)
    plt.savefig(fname)
    self.count += 1
    plt.clf()

  def report(self, data):
    burst_id = data.get('id', 0)
    d = data[self.in_field] if self.in_field else data

    if self.mode:
      if self.mode == 'Gaussian':
        mean = d['mean']
        std = d['std']
        exp_mean = self.true_dist
        exp_std = d['error_std']
        self.render_Gaussian(burst_id, d['xlow'], d['xhigh'], d['bins'], mean, std, exp_mean, exp_std)
    else:
      self.render(burst_id, d['xlow'], d['xhigh'], d['bins'])

    return True

