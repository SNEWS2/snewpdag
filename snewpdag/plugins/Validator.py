'''
This will check that a field has the proper form,
and either clean it up or consume the action.
Then we don't have to have each downstream plugin
repeat this sort of validation.

check_key() checks that the desired key/field exists in the payload

check_type() checks that the field has the correct type,
e.g. 'action': str, 'history': History

check_listtype() checks the type of the elements in the list
based on the type we want in the input,
and if a wrong type is found, such element is removed
and the removal is logged.

check_sorted() is for numbers in a list.
It checks whether it is sorted in ascending/descending order.
If it is not sorted, then it sorts the list based on the order in the input.
We may also pass the list unmodified by not including order in the input.

'''

import logging
import numpy as np
import healpy as hp
from snewpdag.dag import Node

class Validator(Node):
    def __init__(self, **kwargs):
        self.search_key = kwargs.pop('search_key', None)
        self.key_type = kwargs.pop('key_type', None)
        self.order = kwargs.pop('order', None)
        super().__init__(**kwargs)
    
    def check_key(self, data): # check that the key exists
        if self.search_key in data:
            return True
        else:
            logging.error('Desired key [{}] not found in payload'.format(self.search_key))
            return False

    def check_type(self, data): # check that the key corresponed to the correct type
        return isinstance(data, self.key_type)
    
    def check_listtype(self, data): # same as above but we check elements of a list
        remove_element = []
        for x in data:
            if isinstance(x, self.key_type) == False:
                remove_element.append(x)
        for x in remove_element:
            data.remove(x)
            logging.error('{} in list is not the desired type of {} and has been deleted'.format(x, self.key_type))
        return data

    def check_sorted(self, data):
        listorder = None
        if data == sorted(data):
            listorder = 'ascending'
            print('Input is sorted in ascending order')
        elif data == sorted(data, reverse=True):
            listorder = 'descending'
            print('Input is sorted in descending order')

        if self.order:
            if listorder != self.order:
                print('Not sorted in required order -- system will now sort in', self.order, 'order')
                if (self.order == 'ascending'):
                    data.sort()
                elif (self.order == 'descending'):
                    data.sort(reverse=True)
        else:
            print('Not sorted. System will pass on unmodified')
        
        return data
