"""
Node in the directed acyclic graph.
Implemented on observer-observable pattern.

Plugins should subclass Node and override alert, revoke, reset, report.
"""
import logging

from snewpdag.values import History

class Node:

  # shared random number generator - initialized by app
  rng = None

  def __init__(self, name, **kwargs):
    """
    Initialize the node.
    OVERRIDE this method to initialize more instance data.
    At the end call super().__init__(**kwargs) to continue initialization.
    """
    self.name = name     # name of the Node
    self.observers = []  # observers of this Node
    self.watch_list = [] # nodes this Node is observing
    self.last_data = {}  # data after last update
    self.last_source = None # source of last update

  def dispose(self):
    """
    Clear the last data, and detach from all observers and observables.
    """
    self.last_data.clear()
    for n in self.observers:
      self.detach(n)
    for n in self.watch_list:
      n.detach(self)

  def attach(self, observer):
    """
    Register observer (of type Node).
    The observer's notify() is called when this Node is done processing.
    The watch list is only to keep track of inputs.
    """
    if observer not in self.observers:
      self.observers.append(observer)
      observer.watch_list.append(self)

  def detach(self, observer):
    """
    Stop notifications to the specified observer.
    Also removes this node from observer's watch list.
    """
    if observer in self.observers:
      self.observers.remove(observer)
      observer.watch_list.remove(self)

  def notify(self, action, data):
    """
    Notify all observers that they need to update.
    Update history by appending name of current node.
    """
    self.last_data = data.copy() # shallow copy (copies refs of objects)
    # record action
    self.last_data['action'] = action
    # append to history (tuple, so remember that tuples are immutable)
    #if history == None:
    #  if 'history' in data:
    #    h1 = self.last_data['history']
    #  else:
    #    #h1 = ()
    #    h1 = History()
    #else:
    #  h1 = history

    if 'history' not in data:
      self.last_data['history'] = History()
    self.last_data['history'].append(self.name)
    #h2 = (self.name,)
    #self.last_data['history'] = h1 + h2
    # notify all observers
    for obs in self.observers:
      logging.debug('DEBUG:{0}: notify {1}'.format(self.name, obs.name))
      obs.update(self.last_data)

#
# entry points
#   alert, revoke, report, reset are preferred.
#   this update() will invoke one of the four.
#   overriding update() gives full control to the subclass.
#
# alert/revoke/report/reset will be called first.
#   return True if forward action downstream.
#   return False/None if don't forward.
#   return payload to notify downstream.
# notify() will add this node name to the history,
# so if you need to update the payload history,
# just record the past history, i.e., before this node.
#
# These methods are called by update() with their own local shallow
# copy of the payload.  They can therefore modify the contents of the
# payload itself, though underlying mutable objects shouldn't be modified
# (as the modifications will be seen by any plugins executing
# after this one).
#
# Remember that mutable objects in python are list, dict, byte array.
# Immutable objects: int, float, complex, string, tuple, frozen set, bytes.
#

  def alert(self, data):
    """
    Alert action. Override this method to perform calculations.
    """
    return True

  def revoke(self, data):
    """
    Revoke action. Override this method to update calculation.
    """
    return True

  def report(self, data):
    """
    Report action. Override to provide a final answer.
    """
    return True

  def reset(self, data):
    """
    Reset action. Override to clear alert data (revoke all inputs).
    Not used in single-instance calculation, but rather for MC trials.
    """
    return True

  def other(self, data):
    """
    An action not defined by default. Override to implement handling
    a custom alert. By default, it gives an error message and
    consumes (doesn't forward) the alert.
    (Note that action is defined in the payload, because that's how
    we got here in the first place)
    """
    logging.error('{0}: unrecognized action {1}'.format(
                  self.name, data['action']))
    return False

  def update(self, data):
    """
    Update this object with provided data.
    If you know what you're doing, override this method to perform calculations.
      When done, call notify.
      Default method notifies using original data.
      A nontrivial calculation is likely to notify with different data.
    It is preferred to override alert/revoke/report/reset methods.

    This method makes a local shallow copy of the payload before
    calling the action methods.  So it should be all right for an
    action to add to the payload and return it for notification
    (which will make another shallow copy as self.last_data).
    """
    logging.debug('{0}: update({1})'.format(self.name,
                  data['action'] if 'action' in data else 'None'))
    cdata = data.copy() # local shallow copy
    if 'history' in cdata:
      cdata['history'] = data['history'].copy() # local copy of history
      self.last_source = cdata['history'].last()

    if 'action' in cdata:
      action = cdata['action']
      v = False
      if action == 'alert':
        v = self.alert(cdata)
      elif action == 'revoke':
        v = self.revoke(cdata)
      elif action == 'report':
        v = self.report(cdata)
      elif action == 'reset':
        v = self.reset(cdata)
      else:
        v = self.other(cdata)

      if v == True:
        self.notify(action, cdata) # notify() will update history
      elif v == False:
        return
      elif type(v) is dict:
        self.notify(v['action'] if 'action' in v else action, v)
      else:
        logging.error('{0}: empty action response'.format(self.name))
        return
    else:
      logging.error('[{}] Action not specified'.format(self.name))

#
# utility functions
#

  def watch_index(self, source):
    """
    Utility function to find index in watch_list for given source.
    Returns -1 if not found.
    """
    for i in range(len(self.watch_list)):
      if source == self.watch_list[i].name:
        return i

    logging.error('{}: unrecognized source {}'.format(self.name, source))
    return -1

  def last_watch_index(self):
    if self.last_source:
      return self.watch_index(self.last_source)
    logging.error('{}: no payload source'.format(self.name))
    return -1

