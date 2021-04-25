"""
Time profile renderer.

Configuration options:
  title:  profile title (top of plot)
  xfield:  name of data field for x values
  yfield:  name of data field for y values
  xlabel:  x axis label
  ylabel:  y axis label
  filename:  output filename, with fields
             {0} renderer name
             {1} count index, starting from 0
             {2} id from update data (default 0 if no such field)
             {3} source name (which this renderer observes)

Plots y vs x.
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

  def render(self, burst_id, source, x, y, subtitle):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_xlabel(self.xlabel)
    ax.set_ylabel(self.ylabel)
    ax.set_title(self.title + '(' + subtitle + ')')
    fig.tight_layout()

    fname = self.filename.format(self.name, self.count, burst_id, source)
    plt.savefig(fname)
    self.count += 1

  def alert(self, data):
    burst_id = data['id'] if 'id' in data else 0
    nm = data['name']
    if 'comment' in data:
      nm += ": " + data['comment']
    self.render(burst_id, data['history'][-1],
                data[self.xfield], data[self.yfield], nm)
    return True

  def report(self, data):
    return self.alert(data)

