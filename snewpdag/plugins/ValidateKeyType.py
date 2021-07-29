'''
This will check the type of a key/field,
and will consume the action if it's not the right type.
Then we don't have to have each downstream plugin
repeat this sort of validation.

check_type() checks that the field has the correct type,
e.g. 'action': str, 'history': History

Constructor arguments:
    in_field: string, name of field to check from data
    key_type: string, the type of the key/field to check for, e.g. type of 'dt': 'float'
    on_alert: string, to initiate alert; true by default (optional argument)
    on_reset, on_revoke, on_report: string, false by default (optional argument)
'''

from snewpdag.dag import Node

class ValidateKeyType(Node):
    def __init__(self, in_field, key_type, **kwargs):
        self.in_field = in_field
        self.key_type = key_type
        self.on_alert = kwargs.pop('on_alert', True)
        self.on_reset = kwargs.pop('on_reset', False)
        self.on_revoke = kwargs.pop('on_revoke', False)
        self.on_report = kwargs.pop('on_report', False)
        super().__init__(**kwargs)

    def check_type(self, data): # check that the key corresponed to the correct type
        return type(data[self.in_field]).__name__ == self.key_type
    
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