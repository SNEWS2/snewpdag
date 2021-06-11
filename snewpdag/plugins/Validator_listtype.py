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

Input: data as payload + key_type
'''

import logging
from snewpdag.dag import Node

class Validator_listtype(Node):
    def __init__(self, **kwargs):
        self.key_type = kwargs.pop('key_type', None)
        super().__init__(**kwargs)
    
    def check_listtype(self, data): # same as above but we check elements of a list
        data_len = len(data)
        remove_element = []
        for x in data:
            if isinstance(x, self.key_type) == False:
                remove_element.append(x)
        if len(remove_element) <= (data_len*0.1):
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