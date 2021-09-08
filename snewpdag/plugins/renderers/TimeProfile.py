"""
Time profile renderer.

Configuration options:
  in_field:  optional, name of dictionary of input data
             (otherwise look in payload dictionary itself)
  in_xfield:  name of data field for x values
  in_yfield:  name of data field for y values
  title:  profile title (top of plot)
  xlabel:  x axis label
  ylabel:  y axis label
  filename:  output filename, with fields
             {0} renderer name
             {1} count index, starting from 0
             {2} burst_id from update data (default 0 if no such field)
             {3} source name (which this renderer observes)

Plots y vs x.
"""
import matplotlib.pyplot as plt
import numpy as np

from snewpdag.dag import Node

class TimeProfile(Node):
  def __init__(self, in_xfield, in_yfield, title, xlabel, ylabel, filename, **kwargs):
    self.xfield = in_xfield
    self.yfield = in_yfield
    self.title = title
    self.xlabel = xlabel
    self.ylabel = ylabel
    self.filename = filename # include pattern to include index
    self.in_field = kwargs.pop('in_field', None)
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
    burst_id = data.get('burst_id', 0)
    d = data[self.in_field] if self.in_field else data
    nm = d['name']
    if 'comment' in d:
      nm += ": " + d['comment']
    self.render(burst_id, self.last_source,
                d[self.xfield], d[self.yfield], nm)
    return True

  def report(self, data):
    return self.alert(data)

