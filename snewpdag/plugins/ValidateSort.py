'''
This will check whether the numbers in a list are sorted.
Then we don't have to have each downstream plugin
repeat this sort of validation.

check_sorted() is for numbers in a list.
It checks whether it is sorted in ascending/descending order or not sorted.

Constructor arguments:
    in_field: string, name of field to check from data
    list_order: string, the preferred order for the list (optional argument)
    on_alert: string, to initiate alert; true by default (optional argument)
    on_reset, on_revoke, on_report: string, false by default (optional argument)
'''

import logging
from snewpdag.dag import Node

class ValidateSort(Node):
    def __init__(self, in_field, **kwargs):
        self.in_field = in_field
        self.list_order = kwargs.pop('list_order', None)
        self.on_alert = kwargs.pop('on_alert', True)
        self.on_reset = kwargs.pop('on_reset', False)
        self.on_revoke = kwargs.pop('on_revoke', False)
        self.on_report = kwargs.pop('on_report', False)
        super().__init__(**kwargs)
    
    def check_sorted(self, data):
        temp = data[self.in_field][0]
        ascending_flag = 1
        descending_flag = 1
        order = None
        
        for x in data[self.in_field]:
            if x < temp: # check ascending
                ascending_flag = 0
            if x > temp: # check descending
                descending_flag = 0
            temp = x

        if ascending_flag == 1:
            order = 'ascending'
            logging.info('Input is sorted in ascending order')
        elif descending_flag == 1:
            order = 'descending'
            logging.info('Input is sorted in descending order')
        
        if self.list_order:                 # If there is a specified order,
            if order == self.list_order:    # check if the current order is as specified,
                data['order'] = order       # if yes, then add the 'order' field and return data,
                return data                 # otherwise, modify data below to specified order.
        else:                               # If there is no specified order,
            if order:                       # check if there is a pre-existing order,
                data['order'] = order       # if yes, then add the 'order' field
            else:
                data['order'] = None
            return data                 
        
        data_copy = data[self.in_field].copy()
        if self.list_order == 'ascending':
            data_copy.sort()
            logging.info('Input is modified to now sort in ascending order')
        elif self.list_order == 'descending':
            data_copy.sort(reverse=True)
            logging.info('Input is modified to now sort in descending order')
        data[self.in_field] = data_copy
        data['order'] = self.list_order
        return data  
    
    def alert(self, data):
        if self.on_alert:
            return self.check_sorted(data)
        else:
            return False
    
    def revoke(self, data):
        if self.on_revoke:
            return self.check_sorted(data)
        else:
            return False

    def reset(self, data):
        if self.on_reset:
            return self.check_sorted(data)
        else:
            return False

    def report(self, data):
        if self.on_report:
            return self.check_sorted(data)
        else:
            return False