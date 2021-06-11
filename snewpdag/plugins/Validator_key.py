'''
This will check that a certain key/field exists in the payload,
and if not, consume the action.
Then we don't have to have each downstream plugin
repeat this sort of validation.

check_key() checks that the desired key/field exists in the payload

Input: data as payload + search_key
'''

import logging
from snewpdag.dag import Node

class Validator_key(Node):
    def __init__(self, **kwargs):
        self.search_key = kwargs.pop('search_key', None)
        super().__init__(**kwargs)
    
    def check_key(self, data): # check that the key exists
        if self.search_key in data:
            return True
        else:
            logging.error('Desired key [{}] not found in payload and action is consumed'.format(self.search_key))
            return False
    
    def alert(self, data):
        if self.check_key(data):
            return True
        else:
            return False