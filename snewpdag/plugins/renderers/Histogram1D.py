"""
1D Histogram renderer
Configuration options:
  title:  histogram title (top of plot)
  xlabel:  x axis label
  ylabel:  y axis label
  filename:  output filename, with fields
             {0} renderer name
             {1} count index, starting from 0
             {2} burst_id from update data (default 0 if no such field)
  true_dist: true distance if needed (used for Gaussian fitting comparisons)
Might be nice to allow options to be configured here as well.
Input data:
  action - only respond to 'report'
  burst_id - burst identifier
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
from snewpdag.dag.lib import fill_filename

class Histogram1D(Node):
  def __init__(self, title, xlabel, ylabel, filename, **kwargs):
    self.title = title
    self.xlabel = xlabel
    self.ylabel = ylabel
    self.filename = filename # include pattern to include index
    self.in_field = kwargs.pop('in_field', None)
    self.mode = kwargs.pop('mode', None)
    self.count = 0 # number of histograms made
    super().__init__(**kwargs)

  def render(self, fname, burst_id, xlo, xhi, bins):
    n = len(bins)
    step = (xhi - xlo) / n
    x = np.arange(xlo, xhi, step)

    plt.rcParams.update({'font.size': 12})
    
    fig, ax = plt.subplots()
    ax.bar(x, bins, width=step, align='edge')
    #ax.plot(x, bins)
    ax.set_xlabel(self.xlabel,size=15)
    ax.set_ylabel(self.ylabel,size=15)
    ax.set_title('{0} (burst {1} count {2})'.format(
                 self.title, burst_id, self.count))
    fig.tight_layout()

    #fname = self.filename.format(self.name, self.count, burst_id)
    plt.savefig(fname)
    self.count += 1

  def render_Gaussian(self, fname, burst_id, xlo, xhi, bins, mean, std, exp_mean, exp_std):
    n = len(bins)
    step = (xhi - xlo) / n
    x = np.arange(xlo, xhi, step)
    x_Gauss = np.linspace(mean - 3*std, mean + 3*std, 100)
    x_exp_Gauss = np.linspace(exp_mean - 3*exp_std, exp_mean + 3*exp_std, 100)
    
    fig, ax = plt.subplots()
    ax.bar(x, bins, width=step, align='edge')
    ax.set_xlabel(self.xlabel)
    ax.set_ylabel(self.ylabel)
    ax.set_title('{} (burst {} count {})\nGaussian Fit: mean = {:.2f}, std = {:.2f}\nExpected: mean = {:.2f}, std = {:.2f}'
                .format(self.title, burst_id, self.count, mean, std, exp_mean, exp_std))
    fig.tight_layout()

    scale = sum(bins) * step
    plt.plot(x_Gauss, norm.pdf(x_Gauss, mean, std) * scale, linewidth=2, color='r', label='Gaussian Fit')
    plt.plot(x_exp_Gauss, norm.pdf(x_exp_Gauss, exp_mean, exp_std) * scale, linewidth=2, color='g', label='Expected Distrib')
    plt.legend()

    #fname = self.filename.format(self.name, self.count, burst_id, exp_mean)
    plt.savefig(fname)
    self.count += 1
    plt.clf()

  def report(self, data):
    fname = fill_filename(self.filename, self.name, self.count, data)
    if fname == None:
      logging.error('{}: error interpreting {}', self.name, self.filename)
      return False
    burst_id = data.get('burst_id', 0)
    d = data[self.in_field] if self.in_field else data

    if self.mode:
      if self.mode == 'Gaussian':
        mean = d['mean']
        std = d['std']
        exp_mean = data['sn_distance']
        exp_std = d['stats_std']
        self.render_Gaussian(fname, burst_id, d['xlow'], d['xhigh'], d['bins'], mean, std, exp_mean, exp_std)
    else:
      self.render(fname, burst_id, d['xlow'], d['xhigh'], d['bins'])

    return True
