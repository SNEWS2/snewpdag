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

max_fraction is the maximum fraction of numbers with wrong key_type allowed
that we don't need to consume the action.
e.g. max_fraction = 0.1 (i.e. 10%)
I. if there are 10% or fewer elements in the list with wrong key type,
we simply remove the element and log the removal.
II. if there are more than 10% with wrong key type, we consume the action.

Constructor arguments:
    in_field: string, name of field to check from data
    max_fraction: float, see above
    key_type: string, the type of the key/field to check for, e.g. type of 'dt': 'float'
    on_alert: string, to initiate alert; true by default (optional argument)
    on_reset, on_revoke, on_report: string, false by default (optional argument)

Output dictionary:
    alert:
        modify/remove the list in a field if 
'''

import logging
from snewpdag.dag import Node

class ValidateListType(Node):
    def __init__(self, in_field, max_fraction, key_type, **kwargs):
        self.in_field = in_field
        self.max_fraction = max_fraction
        self.key_type = key_type
        self.on_alert = kwargs.pop('on_alert', True)
        self.on_reset = kwargs.pop('on_reset', False)
        self.on_revoke = kwargs.pop('on_revoke', False)
        self.on_report = kwargs.pop('on_report', False)
        super().__init__(**kwargs)
    
    def check_listtype(self, data): # same as above but we check elements of a list
        data_len = len(data[self.in_field])
        data_copy = data[self.in_field].copy()
        remove_element = []
        for x in data_copy:
            if type(x).__name__ != self.key_type:
                remove_element.append(x)
        if len(remove_element) <= (data_len * self.max_fraction):
            logging.error('{} elements in list are not the desired type of {} and are deleted'.format(len(remove_element), self.key_type))
            for x in remove_element:
                data_copy.remove(x)
            data[self.in_field] = data_copy
            return data
        else:
            logging.error('More than 10% in list are not the desired type of {} and action is consumed'.format(self.key_type))
            return False
    
    def alert(self, data):
        if self.on_alert:
            return self.check_listtype(data)
        else:
            return False
    
    def revoke(self, data):
        if self.on_revoke:
            return self.check_listtype(data)
        else:
            return False

    def reset(self, data):
        if self.on_reset:
            return self.check_listtype(data)
        else:
            return False

    def report(self, data):
        if self.on_report:
            return self.check_listtype(data)
        else:
            return False