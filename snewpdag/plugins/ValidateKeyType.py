'''
This will check the type of a key/field,
and will consume the action if it's not the right type.
Then we don't have to have each downstream plugin
repeat this sort of validation.

check_type() checks that the field has the correct type,
e.g. 'action': str, 'history': History

Input: data as payload + key_type
'''

from snewpdag.dag import Node

class ValidateKeyType(Node):
    def __init__(self, **kwargs):
        self.key_type = kwargs.pop('key_type', None)
        super().__init__(**kwargs)

    def check_type(self, data): # check that the key corresponed to the correct type
        return isinstance(data, self.key_type)
    
    def alert(self, data):
        return self.check_type(data)