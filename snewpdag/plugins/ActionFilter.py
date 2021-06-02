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
import numpy as np
import healpy as hp
from snewpdag.dag import Node

class ActionFilter(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def alert(self, data):
        # if 'newaction' in data: (this line does not work for some reason)
        if len(data) > 1 and data['newaction'] == 'alert':
                return True
        else:
            return False # don't forward an alert

    def reset(self, data):
        if len(data) > 1 and data['newaction'] == 'reset':
                return True
        else:
            return False

    def revoke(self, data):
        if len(data) > 1 and data['newaction'] == 'revoke':
                return True
        else:
            return False

    def report(self, data):
        if len(data) > 1 and data['newaction'] == 'report':
                return True
        else:
            return False
    
    def change_action(self, data):
        self.alert(data)
        self.reset(data)
        self.revoke(data)
        self.report(data)
