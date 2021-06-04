"""
TimeDistInput:  plugin which takes time distribution data.

This just validates that, if the data is an alert, it has the following
fields:
* t_bins: array of floats, event counts in each time bin
* t_low: float or array of floats. If an array of floats, it should
         have the same length as t_bins
* t_high: float. Should be greater than t_low or last value of t_low
"""
import logging

from snewpdag.dag import Node

class TimeDistInput(Node):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)

  def alert(self, data):
    """
    Check that the input has the right fields:
    - if it's an alert, it should have a times field.
    - if it's not an alert, just pass it along.
    """
    logging.info("[{}] update called".format(self.name))
    if 't_bins' in data and 't_low' in data and 't_high' in data:
      if np.isscalar(data['t_low']):
        # might be nice to check that all the entries in t_bins
        # are floats
        if data['t_low'] < data['t_high']:
          return True
        else:
          logger.error('[{}]: t_low {} greater than t_high {}'.format(
                       self.name, data['t_low'], data['t_high']))
      else:
        if len(data['t_bins']) == len(data['t_low']) and \
            data['t_low'][-1] < data['t_high']:
          return True
        else:
          logger.error('[{}] problem in time histogram'.format(self.name))
    else:
      logging.error('[{}] Expected fields not found'.format(self.name))
    return False

