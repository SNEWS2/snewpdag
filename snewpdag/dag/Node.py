"""
Node in the directed acyclic graph.
Implemented on observer-observable pattern.

Plugins should subclass Node and override update().
"""
import logging

class Node:

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

  def reset(self):
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

  def notify(self, action, history, data):
    """
    Notify all observers that they need to update.
    Update history by appending name to data field.
    Previous history is given by history argument,
    but if history == None, data['history'] will be used
    as the starting point.
    """
    self.last_data = data.copy()
    # record action
    self.last_data['action'] = action
    # append to history
    if history == None:
      if 'history' in data:
        h1 = self.last_data['history']
      else:
        h1 = ()
    else:
      h1 = history
    h2 = (self.name,)
    self.last_data['history'] = h1 + h2
    # notify all observers
    for obs in self.observers:
      obs.update(self.last_data)

  def update(self, data):
    """
    Update this object with provided data.
    OVERRIDE this method to perform calculations.
    When done, call notify.
    Default method notifies using original data.
    A nontrivial calculation is likely to notify with different data.
    """
    if 'action' in data:
      self.notify(data['action'], None, data)
    else:
      logging.error('[{}] Action not specified'.format(self.name))

  def watch_index(self, source):
    """
    Utility function to find index in watch_list for given source.
    Returns -1 if not found.
    """
    for i in range(len(self.watch_list)):
      if source == self.watch_list[i].name:
        return i
    return -1

