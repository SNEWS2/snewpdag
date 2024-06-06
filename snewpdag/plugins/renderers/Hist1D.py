"""
Hist1D - render a Hist1D object

Arguments:
  in_field:  field name containing Hist1D
  title:  histogram title (top of plot)
  xlabel:  x axis label
  ylabel:  y axis label
  filename:  output filename, with fields
             {0} renderer name
             {1} count index, starting from 0
             {2} burst_id from update data (default 0 if no such field)
  scriptname:  output script name, with fields; None if not used (default)
  on (optional): list of 'alert', 'reset', 'revoke', 'report'
    (default ['report'])
Might be nice to allow options to be configured here as well.

Input data:
  action - only respond to 'report'
  burst_id - burst identifier
  xlow
  xhigh
  bins - uniform bin contents
"""
import logging
import json
#import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from snewpdag.dag import Node
from snewpdag.dag.lib import fill_filename, fetch_field

class Hist1D(Node):
  def __init__(self, in_field, title, xlabel, ylabel, filename, **kwargs):
    self.in_field = in_field
    self.title = title
    self.xlabel = xlabel
    self.ylabel = ylabel
    self.filename = filename # include pattern to include index
    self.scriptname = kwargs.pop('scriptname', None)
    self.on = kwargs.pop('on', ['report'])
    self.count = 0 # number of histograms made
    super().__init__(**kwargs)

  def plot(self, fname, sname, burst_id, hist):
    logging.debug('Hist1D.plot called')
    make_script = (sname != None)
    if make_script:
      sfile = open(sname, 'w')
      sfile.write('import numpy as np\n')
      sfile.write('import matplotlib.pyplot as plt\n')
      sfile.write('# Script:    {}\n'.format(sname))
      sfile.write('# Image:     {}\n'.format(fname))
      sfile.write('# count = {}, mean = {}, rms = {}\n'.format(hist.count, hist.mean(), np.sqrt(hist.variance())))
      sfile.write('# underflow = {}, overflow = {}\n'.format(hist.underflow, hist.overflow))
    print('=====================')
    print('H Filename:  {}'.format(fname))
    print('H Title:     {}'.format(self.title))
    print('H Entries:   {}'.format(hist.count))
    #print('H Sum:       {}'.format(hist.sum))
    print('H Mean:      {}'.format(hist.mean()))
    print('H RMS:       {}'.format(np.sqrt(hist.variance())))
    print('H Overflow:  {}'.format(hist.overflow))
    print('H Underflow: {}'.format(hist.underflow))
    print('=====================')

    step = (hist.xhigh - hist.xlow) / hist.nbins
    x = np.arange(hist.xlow, hist.xhigh, step)

    #plt.rcParams.update({'font.size': 12})
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)

    #fig, ax = plt.subplots()
    ax.bar(x, hist.bins, width=step, align='edge')
    #ax.plot(x, bins)
    ax.set_xlabel(self.xlabel,size=15)
    ax.set_ylabel(self.ylabel,size=15)
    ax.set_title('{0} (burst {1} count {2})'.format(
                 self.title, burst_id, self.count))
    fig.tight_layout()

    #plt.savefig(fname)
    canvas.print_png(fname)

    if make_script:
      sfile.write("plt.rcParams.update({'font.size': 12})\n")
      sfile.write('x = np.arange({}, {}, {})\n'.format(hist.xlow, hist.xhigh, step))
      sfile.write('bins = {}\n'.format(hist.bins.tolist()))
      sfile.write('fig, ax = plt.subplots()\n')
      sfile.write("ax.bar(x, bins, width={}, align='edge')\n".format(step))
      sfile.write("ax.set_xlabel('{}', size=15)\n".format(self.xlabel))
      sfile.write("ax.set_ylabel('{}', size=15)\n".format(self.ylabel))
      sfile.write("ax.set_title('{} (burst {} count {})')\n".format(self.title, burst_id, self.count))
      sfile.write('fig.tight_layout()\n')
      sfile.write('plt.show()\n')
      #sfile.write('plt.savefig("{}")\n'.format(fname))
      sfile.close()

    self.count += 1

  def render(self, data):
    logging.debug('Hist1D.render called')
    hist, exists = fetch_field(data, self.in_field)
    if exists:
      # TODO: foregoing check that hist is a values.Hist1D
      # because I can't figure out how to use isinstance
      # for a class in a module (!)
      burst_id = data.get('burst_id', 0)
      fname = fill_filename(self.filename, self.name, self.count, data)
      if fname == None:
        logging.error('{}: error interpreting {}'.format(self.name, self.filename))
        return False
      sname = None if self.scriptname == None else \
              fill_filename(self.scriptname, self.name, self.count, data)
      self.plot(fname, sname, burst_id, hist)
    return True # always return True

  def alert(self, data):
    return self.render(data) if 'alert' in self.on else True

  def revoke(self, data):
    return self.render(data) if 'revoke' in self.on else True

  def reset(self, data):
    return self.render(data) if 'reset' in self.on else True

  def report(self, data):
    return self.render(data) if 'report' in self.on else True

