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

Might be nice to allow options to be configured here as well.

Input data:
  action - only respond to 'report'
  id - burst id
  histogram.xlow
  histogram.xhigh
  histogram.bins - uniform bin contents
"""
import matplotlib.pyplot as plt
import numpy as np

from snewpdag.dag import Node

class Histogram1D(Node):
  def __init__(self, title, xlabel, ylabel, filename, **kwargs):
    self.title = title
    self.xlabel = xlabel
    self.ylabel = ylabel
    self.filename = filename # include pattern to include index
    self.count = 0 # number of histograms made
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
    ax.set_title(self.title)
    fig.tight_layout()

    fname = self.filename.format(self.name, self.count, burst_id)
    plt.savefig(fname)
    self.count += 1

  def update(self, data):
    action = data['action']
    if action == 'report':
      h = data['histogram']
      burst_id = data['id'] if 'id' in data else 0
      self.render(burst_id, h['xlow'], h['xhigh'], h['bins'])
    self.notify(action, None, data)

