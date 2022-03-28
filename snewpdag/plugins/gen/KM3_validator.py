import logging
from snewpdag.dag import Node

class KM3_validator(Node):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def alert(self, data):
        for coinc_detector in data['detector_names']:
            if coinc_detector == 'KM3':
                logging.info('FOUND KM3 DATA')
                data['det_data'] = 'KM3'
                #### Add other conditions to veryfy the completness of the data

                return True
        return False