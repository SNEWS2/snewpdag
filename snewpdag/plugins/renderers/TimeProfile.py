"""
Time profile renderer.

Plots y vs x.
Filename arguments:  name, source, count
"""
import matplotlib.pyplot as plt
import numpy as np

from snewpdag.dag import Node

class TimeProfile(Node):
  def __init__(self, xfield, yfield, title, xlabel, ylabel, filename, **kwargs):
    self.xfield = xfield
    self.yfield = yfield
    self.title = title
    self.xlabel = xlabel
    self.ylabel = ylabel
    self.filename = filename # include pattern to include index
    self.count = 0 # number of histograms made
    super().__init__(**kwargs)

  def render(self, source, x, y, subtitle):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_xlabel(self.xlabel)
    ax.set_ylabel(self.ylabel)
    ax.set_title(self.title + '(' + subtitle + ')')
    fig.tight_layout()

    fname = self.filename.format(self.name, source, self.count)
    plt.savefig(fname)
    self.count += 1

  def update(self, data):
    action = data['action']
    if action == 'report' or action == 'alert':
      nm = data['name']
      if 'comment' in data:
        nm += ": " + data['comment']
      self.render(data['history'][-1], data[self.xfield], data[self.yfield], nm)
    self.notify(action, None, data)

