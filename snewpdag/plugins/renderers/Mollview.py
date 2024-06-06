"""
Mollview - primitive skymap image

Arguments:
  in_field: payload field name for skymap
  title: title to put on image
  units: unit label text
  coord: 'C' celestial, 'E' ecliptic, 'G' galactic; list of conversion
  filename: output filename, {0} module name, {1} count, {2} burst_id
  range: (optional, default none), none, (min,) or (min,max)
  min: minimum value (default 0)
  max: maximum value (default -1). If max <= min, get max from data
  on: list of 'alert', 'reset', 'revoke', 'report' (default ['alert'])
"""
import logging
import matplotlib.pyplot as plt
import numpy as np
import healpy as hp

from snewpdag.dag import Node
from snewpdag.dag.lib import fill_filename, fetch_field
from snewpdag.values import LMap

class Mollview(Node):
  def __init__(self, in_field, title, units, coord, filename, **kwargs):
    self.in_field = in_field
    self.title = title
    self.units = units
    self.coord = coord
    self.filename = filename
    self.range = kwargs.pop('range', None)
    #self.min = kwargs.pop('min', 0)
    #self.max = kwargs.pop('max', -1)
    self.on = kwargs.pop('on', ['alert'])
    self.scriptname = kwargs.pop('scriptname', None)
    self.count = 0
    super().__init__(**kwargs)

  def plot(self, data):
    sname = None if self.scriptname == None else \
            fill_filename(self.scriptname, self.name, self.count, data)
    make_script = (sname != None)
    fname = fill_filename(self.filename, self.name, self.count, data)
    if fname == None:
      logging.error('{}: error interpreting {}'.format(self.name, self.filename))
      return False

    if make_script:
      sfile = open(sname, 'w')
      sfile.write('import numpy as np\n')
      sfile.write('import healpy as hp\n')
      sfile.write('import matplotlib.pyplot as plt\n')
      sfile.write('# Script:    {}\n'.format(sname))
      sfile.write('# Image:     {}\n'.format(fname))

    m, exists = fetch_field(data, self.in_field)
    if exists:
      # replace a lot of these options later
      kwargs = {}
      if isinstance(self.range, (list, tuple, np.ndarray)):
        if len(self.range) >= 1:
          kwargs['min'] = self.range[0]
        if len(self.range) >= 2:
          kwargs['max'] = self.range[1]
      hp.mollview(m,
                  coord=self.coord,
                  title=self.title,
                  unit=self.units,
                  #min=self.min,
                  #max=self.max,
                  nest=True,
                  **kwargs,
                 )
      hp.graticule()
      plt.savefig(fname)
      plt.close()

      if make_script:
        sfile.write('kwargs = {}\n'.format(kwargs))
        sfile.write('m = np.array({})\n'.format(m.tolist()))
        sfile.write("hp.mollview(m, coord={}, title='{}', unit='{}', nest=True, **kwargs)\n".format(self.coord, self.title, self.units))
        sfile.write('hp.graticule()\n')
        sfile.write('plt.show()\n')
        sfile.close()

      self.count += 1
    return True

  def alert(self, data):
    logging.debug('{}: alert'.format(self.name))
    return self.plot(data) if 'alert' in self.on else True

  def revoke(self, data):
    logging.debug('{}: revoke'.format(self.name))
    return self.plot(data) if 'revoke' in self.on else True

  def reset(self, data):
    logging.debug('{}: reset'.format(self.name))
    return self.plot(data) if 'reset' in self.on else True

  def report(self, data):
    logging.debug('{}: report'.format(self.name))
    return self.plot(data) if 'report' in self.on else True

