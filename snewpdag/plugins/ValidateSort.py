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
    def __init__(self, listorder, **kwargs):
        self.listorder = listorder
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
            self.listorder = 'ascending'
            print('Input is sorted in ascending order')
        elif descending_flag == 1:
            self.listorder = 'descending'
            print('Input is sorted in descending order')
        else:
            self.listorder = None
            print('Input is not sorted.')
        
        return self.listorder