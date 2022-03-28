import logging
from snewpdag.dag import Node

class Baksan_validator(Node):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def alert(self, data):
        for coinc_detector in data['detector_names']:
            if coinc_detector == 'Baksan':
                logging.info('FOUND Baksan DATA')
                data['det_data'] = 'Baksan'
                #### Add other conditions to veryfy the completness of the data

                return True
        return False


