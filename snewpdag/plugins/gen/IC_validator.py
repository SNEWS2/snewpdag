import logging
from snewpdag.dag import Node

class IC_validator(Node):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def alert(self, data):
        for coinc_detector in data['detector_names']:
            if coinc_detector == 'IC':
                logging.info('FOUND IC DATA')
                data['det_data'] = 'IC'
                #### Add other conditions to veryfy the completness of the data

                return True
        return False

