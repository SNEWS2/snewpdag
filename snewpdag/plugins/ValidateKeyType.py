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
        if type(data).__name__ == self.key_type:
            return True
        else:
            return False
    
    def alert(self, data):
        return self.check_type(data)