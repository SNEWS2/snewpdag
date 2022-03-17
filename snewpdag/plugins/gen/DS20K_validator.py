import logging
from snewpdag.dag import Node

class DS20K_validator(Node):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def alert(self, data):
        for coinc_detector in data['detector_names']:
            if coinc_detector == 'DS-20KnT':
                logging.info('FOUND DS-20K DATA')
                data['det_data'] = 'DS-20K'
                #### Add other conditions to veryfy the completness of the data

                return data
        return False
