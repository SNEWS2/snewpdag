'''
This will check whether the numbers in a list are sorted.
Then we don't have to have each downstream plugin
repeat this sort of validation.

check_sorted() is for numbers in a list.
It checks whether it is sorted in ascending/descending order or not sorted.

Input: data as payload
'''

from snewpdag.dag import Node

class ValidateSort(Node):
    def __init__(self, list_order, **kwargs):
        self.list_order = list_order
        self.on_alert = kwargs.pop('on_alert', None)
        self.on_reset = kwargs.pop('on_reset', None)
        self.on_revoke = kwargs.pop('on_revoke', None)
        self.on_report = kwargs.pop('on_report', None)
        super().__init__(**kwargs)
    
    def check_sorted(self, data):
        temp = data[0]
        ascending_flag = 1
        descending_flag = 1

        for x in data:
            if x < temp: # check ascending
                ascending_flag = 0
            if x > temp: # check descending
                descending_flag = 0
            temp = x

        if ascending_flag == 1:
            self.list_order = 'ascending'
            print('Input is sorted in ascending order')
        elif descending_flag == 1:
            self.list_order = 'descending'
            print('Input is sorted in descending order')
        else:
            self.list_order = None
            print('Input is not sorted.')
        
        return self.list_order
    
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