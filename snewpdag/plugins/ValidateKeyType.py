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
        self.on_alert = kwargs.pop('on_alert', None)
        self.on_reset = kwargs.pop('on_reset', None)
        self.on_revoke = kwargs.pop('on_revoke', None)
        self.on_report = kwargs.pop('on_report', None)
        super().__init__(**kwargs)

    def check_type(self, data): # check that the key corresponed to the correct type
        return type(data).__name__ == self.key_type
    
    def alert(self, data):
        if self.on_alert:
            return self.check_type(data)
        else:
            return False
    
    def revoke(self, data):
        if self.on_revoke:
            return self.check_type(data)
        else:
            return False

    def reset(self, data):
        if self.on_reset:
            return self.check_type(data)
        else:
            return False

    def report(self, data):
        if self.on_report:
            return self.check_type(data)
        else:
            return False