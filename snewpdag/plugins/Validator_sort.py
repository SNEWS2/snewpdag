'''
This will check whether the numbers in a list are sorted.
Then we don't have to have each downstream plugin
repeat this sort of validation.

check_sorted() is for numbers in a list.
It checks whether it is sorted in ascending/descending order or not sorted.

Input: data as payload
'''

from snewpdag.dag import Node

class Validator_sort(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def check_sorted(self, data):
        listorder = None
        if data == sorted(data):
            listorder = 'ascending'
            print('Input is sorted in ascending order')
        elif data == sorted(data, reverse=True):
            listorder = 'descending'
            print('Input is sorted in descending order')
        else:
            print('Input is not sorted.')
        
        return listorder