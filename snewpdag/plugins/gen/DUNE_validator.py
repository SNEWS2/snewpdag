import logging
from snewpdag.dag import Node

class DUNE_validator(Node):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def alert(self, data):
        for coinc_detector in data['detector_names']:
            if coinc_detector == 'DUNE':
                logging.info('FOUND DUNE DATA')
                data['det_data'] = 'DUNE'
                #### Add other conditions to veryfy the completness of the data

                return data
        return False
