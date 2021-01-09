"""
TimeDistInput:  plugin which takes time distribution data.

This just validates that, if the data is an alert, it has a 't'
field to store an array of times, and an 'n' field for event counts,
and that they have the same number of elements.

If the data is a revocation, no such check is performed.
"""
import logging

from snewpdag.dag import Node

class TimeDistInput(Node):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)

  def update(self, data):
    """
    Check that the input has the right fields:
    - if it's an alert, it should have a times field.
    - if it's not an alert, just pass it along.
    """
    logging.info("[{}] update called".format(self.name))
    if 'action' in data:
      if data['action'] == 'alert':
        if 't' in data and 'n' in data:
          if len(data['t']) == len(data['n']):
            logging.info("[{}] notify called".format(self.name))
            self.notify(data['action'], None, data)
          else:
            logging.error('[{}] t and n length mistmatch'.format(self.name))
        else:
          logging.error('[{}] Expected fields not found'.format(self.name))
    else:
      logging.error('[{}] Expected action field not found'.format(self.name))

