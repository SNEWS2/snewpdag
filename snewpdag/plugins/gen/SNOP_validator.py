import logging
from snewpdag.dag import Node

class SNOP_validator(Node):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def alert(self, data):
        for coinc_detector in data['detector_names']:
            if coinc_detector == 'SNOP':
                logging.info('FOUND SNOP DATA')
                data['det_data'] = 'SNOP'
                #### Add other conditions to veryfy the completness of the data

                return True
        return False

