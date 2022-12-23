'''
ScatterPlot renderer

Constructor arguments:
    title:  string, plot title (top of plot)
    xlabel:  string, x axis label
    ylabel:  string, y axis label
    filename:  string, output filename, with fields
                {0} renderer name
    x_in_field: string, name of field with array for x axis (default: x_array)
    x_in_field2: string, secondary field if needed
    y_in_field: string, name of field with array for y axis (default: y_array)
    y_in_field2: string, secondary field if needed
    plot_line: string, line to be plotted on top (as a function of x, e.g. '0*x+4' for y=4,'2*x**2+3' for y=2x^2+3) (optional)
    flags: list of strings (default: off for all flags)
        logx: log scale on x axis
        logy: log scale on y axis

'''

import logging
import matplotlib.pyplot as plt
import numpy as np

from snewpdag.dag import Node
from snewpdag.values import TimeSeries

class ScatterPlot(Node):
    def __init__(self, title, xlabel, ylabel, filename, **kwargs):
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.filename = filename # include pattern to include index
        self.x_in_field = kwargs.pop("x_in_field", "x_array")
        self.x_in_field2 = kwargs.pop("x_in_field2", None)
        self.y_in_field = kwargs.pop("y_in_field", "y_array")
        self.y_in_field2 = kwargs.pop("y_in_field2", None)
        self.line = kwargs.pop("plot_line", None)
        f = kwargs.pop('flags', [])
        self.logx = "logx" in f
        self.logy = "logy" in f
        super().__init__(**kwargs)

    def render(self, fname, x, y):
        fig, ax = plt.subplots()
        ax.plot(x, y, 'x')
        if self.line != None:
            y_line = eval(self.line)
            ax.plot(x, y_line, '-r', label= 'y = '+ self.line)

        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.set_title('{0}'.format(self.title))
        if self.logx: ax.set_xscale('log')
        if self.logy: ax.set_yscale('log')
        if self.line != None: plt.legend()
        fig.tight_layout()
        plt.savefig(fname)        

    def report(self, data):
        x = data[self.x_in_field][self.x_in_field2] if self.x_in_field2 != None else data[self.x_in_field]
        y = data[self.y_in_field][self.y_in_field2] if self.y_in_field2 != None else data[self.y_in_field]
        fname = fill_filename(self.filename, self.name, 0, data)
        if fname == None:
          logging.error('{}: error interpreting {}', self.name, self.filename)
        else:
          self.render(fname, x, y)
        #logging.info('{0}:{1}'.format(self.x_in_field, x))
        #logging.info('{0}:{1}'.format(self.y_in_field, np.around(y, decimals=2)))
        return True

