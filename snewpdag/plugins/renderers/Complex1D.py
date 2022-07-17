"""
Complex1D Renderer

Should add x axis field as well

Arguments:
  in_field
  binrange:  (min,max) bin numbers
  title
  filename
    {0} renderer name
    {1} count index, starting from 0
    {2} burst_id from update data (default 0 if no such field)
  on (optional):  action
"""
import logging
import matplotlib.pyplot as plt
import numpy as np

from snewpdag.dag import Node
from snewpdag.dag.lib import fetch_field

class Complex1D(Node):
  def __init__(self, in_field, binrange, title, filename, **kwargs):
    self.in_field = in_field
    self.b0 = binrange[0]
    self.b1 = binrange[1]
    self.title = title
    self.filename = filename
    self.on = kwargs.pop('on', ['report'])
    self.count = 0
    super().__init__(**kwargs)

  def plots(self, burst_id, ft):
    x = np.arange(len(ft))
    fig, ((axr, axi), (axm, axp)) = plt.subplots(2, 2)

    axr.plot(x[self.b0:self.b1], np.real(ft[self.b0:self.b1]), 'bo')
    axi.plot(x[self.b0:self.b1], np.imag(ft[self.b0:self.b1]), 'ro')
    axm.plot(x[self.b0:self.b1], np.abs(ft[self.b0:self.b1]), 'go')
    axp.plot(x[self.b0:self.b1], np.angle(ft[self.b0:self.b1]), 'mo')
    fig.tight_layout()
    fname = self.filename.format(self.name, self.count, burst_id)
    plt.savefig(fname)
    self.count += 1

  def render(self, data):
    v, flag = fetch_field(data, self.in_field)
    if flag:
      burst_id = data.get('burst_id', 0)
      self.plots(burst_id, v)
    return True

  def alert(self, data):
    return self.render(data) if 'alert' in self.on else True

  def revoke(self, data):
    return self.render(data) if 'revoke' in self.on else True

  def reset(self, data):
    return self.render(data) if 'reset' in self.on else True

  def report(self, data):
    return self.render(data) if 'report' in self.on else True

