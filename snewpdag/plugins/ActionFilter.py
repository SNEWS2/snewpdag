"""
Action Filter: 
This would respond to an action by consuming it (not passing it downstream),
or by changing it to another type of action. For instance, it might be used
to consume alert actions and pass only report actions during an MC trial,
whereas in the actual SNEWS context, we would want plots to be made for every alert.

Input:
(Initial) actions

Output:
Depending on the newaction, choose which action to output.
If no newaction exists, then the initial action is consumed by default.
"""

import logging
from snewpdag.dag import Node

class ActionFilter(Node):
    def __init__(self, **kwargs):
        self.on_alert = kwargs.pop('on_alert', None)
        self.on_reset = kwargs.pop('on_reset', None)
        self.on_revoke = kwargs.pop('on_revoke', None)
        self.on_report = kwargs.pop('on_report', None)
        super().__init__(**kwargs)

    def alert(self, data):
        if self.on_alert:
            data['action'] = self.on_alert
            return data
        else:
            return False # don't forward an alert

    def reset(self, data):
        if self.on_reset:
            data['action'] = self.on_reset
            return data
        else:
            return False

    def revoke(self, data):
        if self.on_revoke:
            data['action'] = self.on_revoke
            return data
        else:
            return False

    def report(self, data):
        if self.on_report:
            data['action'] = self.on_report
            return data
        else:
            return False
    
    '''
    def change_action(self, data): # not sure if this part is really necessary
        self.alert(data)
        self.reset(data)
        self.revoke(data)
        self.report(data)
    '''
