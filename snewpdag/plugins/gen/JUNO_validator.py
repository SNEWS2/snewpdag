import logging
from snewpdag.dag import Node

class JUNO_validator(Node):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def alert(self, data):
        for coinc_detector in data['detector_names']:
            if coinc_detector == 'JUNO':
                logging.info('FOUND JUNO DATA')
                data['det_data'] = 'JUNO'
                #### Add other conditions to veryfy the completness of the data

                return True
        return False
