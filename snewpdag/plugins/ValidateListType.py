'''
This will check the types of the elements in a list,
and will consume the action if
more than 10% of the data are not the right type.
Then we don't have to have each downstream plugin
repeat this sort of validation.

check_listtype() checks the type of the elements in the list
based on the type we want in the input,
and if a wrong type is found, such element is removed
and the removal is logged.

min_fraction is the maximum fraction of numbers with wrong key_type allowed
that we don't need to consume the action.
e.g. min_fraction = 0.1 (i.e. 10%)
I. if there are 10% or fewer elements in the list with wrong key type,
we simply remove the element and log the removal.
II. if there are more than 10% with wrong key type, we consume the action.

Input: data as payload + min_fraction + key_type
'''

import logging
from snewpdag.dag import Node

class ValidateListType(Node):
    def __init__(self, max_fraction, key_type, **kwargs):
        self.max_fraction = max_fraction
        self.key_type = key_type
        super().__init__(**kwargs)
    
    def check_listtype(self, data): # same as above but we check elements of a list
        data_len = len(data)
        remove_element = []
        for x in data:
            if type(x).__name__ != self.key_type:
                remove_element.append(x)
        if len(remove_element) <= (data_len * self.max_fraction):
            logging.error('{} elements in list are not the desired type of {} and are deleted'.format(len(remove_element), self.key_type))
            for x in remove_element:
                data.remove(x)
            return data
        else:
            logging.error('More than 10% in list are not the desired type of {} and action is consumed'.format(self.key_type))
            return False
    
    def alert(self, data):
        if self.check_listtype(data) != False:
            return True
        else:
            return False
    
    def revoke(self, data):
        if self.check_listtype(data) != False:
            return True
        else:
            return False

    def reset(self, data):
        if self.check_listtype(data) != False:
            return True
        else:
            return False

    def report(self, data):
        if self.check_listtype(data) != False:
            return True
        else:
            return False