"""
MultiPlot - make a variety of scatter plots

Arguments:
  in_fields: list of payload field names.  Each element is either a list
    with the form [x,y,opt], x and y being the field name tuple;
    or a single tuple which indicates a Hist1D object.
  title: title to put on image
  xlabel:  x axis label
  ylabel:  y axis label
  filename:  output filename, with fields
  scriptname:  output script name, with fields; None if not used (default)
  on:  list of 'alert', 'reset', 'revoke', 'report' (default ['report'])
"""
import logging
#import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from snewpdag.dag import Node
from snewpdag.dag.lib import fill_filename, fetch_field

class MultiPlot(Node):
  def __init__(self, in_fields, title, xlabel, ylabel, filename, **kwargs):
    self.in_fields = in_fields
    self.title = title
    self.xlabel = xlabel
    self.ylabel = ylabel
    self.filename = filename # include pattern to include index
    self.scriptname = kwargs.pop('scriptname', None)
    self.on = kwargs.pop('on', ['report'])
    self.count = 0 # number of histograms made
    super().__init__(**kwargs)

  def plots(self, data, fname, sname, burst_id):
    make_script = (sname != None)
    if make_script:
      sfile = open(fname, 'w')
      sfile.write('import numpy as np\n')
      sfile.write('import matplotlib.pyplot as plt\n')
      sfile.write('# Script:    {}\n'.format(sname))
      sfile.write('# Image:     {}\n'.format(fname))

    print('=====================')
    print('H Filename:  {}'.format(fname))
    if make_script:
      print('H Script:    {}'.format(sname))
    print('H Title:     {}'.format(self.title))
    #fig, ax = plt.subplots()
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    for f in self.in_fields:
      if isinstance(f, list):
        # assume list is of form [x,y,opt] names
        if len(f) > 2:
          x, exists = fetch_field(data, f[0])
          if exists:
            y, exists = fetch_field(data, f[1])
            if exists:
              opt = f[2]
              ax.plot(x, y, opt)
              if make_script:
                sfile.write('x = np.array({})\n'.format(x.tolist()))
                sfile.write('y = np.array({})\n'.format(y.tolist()))
                sfile.write('fig, ax = plt.subplots()\n')
                sfile.write("ax.plot(x, y, '{}')\n".format(opt))
            else:
              logging.error('{}: y field {} not found'.format(
                            self.name, f[1]))
          else:
            logging.error('{}: x field {} not found'.format(
                          self.name, f[1]))
        else:
          logging.error('{}: invalid field specification {}'.format(
                        self.name, f))

      else:
        # assume it's a Hist1D object
        m, exists = fetch_field(data, f)
        if exists:
          step = (m.xhigh - m.xlow) / m.nbins
          x = np.arange(m.xlow, m.xhigh, step)
          ax.bar(x, m.bins, width=step, align='edge')
          if make_script:
            sfile.write('# count = {}, mean = {}, rms = {}\n'.format(m.count, m.mean(), np.sqrt(m.variance())))
            sfile.write('# underflow = {}, overflow = {}\n'.format(m.underflow, m.overflow))
            sfile.write('x = np.arange({}, {}, {})\n'.format(m.xlow, m.xhigh, step))
            sfile.write('bins = np.array({})\n'.format(m.bins))
            sfile.write('fig, ax = plt.subplots()\n')
            sfile.write("ax.bar(x, bins, width={}, align='edge')\n".format(step))
        else:
          logging.error('{}: Hist1D field {} not found'.format(
                        self.name, f))
    print('=====================')

    ax.set_xlabel(self.xlabel, size=15)
    ax.set_ylabel(self.ylabel, size=15)
    ax.set_title('{0} (burst {1} count {2})'.format(
                 self.title, burst_id, self.count))
    fig.tight_layout()
    #plt.savefig(fname)
    canvas.print_png(fname)
    if make_script:
      sfile.write("ax.set_xlabel('{}', size=15)\n".format(self.xlabel))
      sfile.write("ax.set_ylabel('{}', size=15)\n".format(self.ylabel))
      sfile.write("ax.set_title('{} (burst {} count {})')\n".format(self.title, burst_id, self.count))
      sfile.write('fig.tight_layout()\n')
      sfile.write('plt.show()\n')
      sfile.close()
    self.count += 1

  def render(self, data):
    burst_id = data.get('burst_id', 0)
    fname = fill_filename(self.filename, self.name, self.count, data)
    if fname == None:
      logging.error('{}: error interpreting {}', self.name, self.filename)
      return False
    sname = None if self.scriptname == None else \
            fill_filename(self.scriptname, self.name, self.count, data)
    self.plots(data, fname, sname, burst_id)
    return True

  def alert(self, data):
    return self.render(data) if 'alert' in self.on else True

  def revoke(self, data):
    return self.render(data) if 'revoke' in self.on else True

  def reset(self, data):
    return self.render(data) if 'reset' in self.on else True

  def report(self, data):
    return self.render(data) if 'report' in self.on else True

