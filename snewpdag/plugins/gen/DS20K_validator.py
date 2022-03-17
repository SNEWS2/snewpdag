import logging
from snewpdag.dag import Node

class DS20K_validator(Node):

    def __init__(self, **kwargs):
        #index = self.last_watch_index()
        super().__init__(**kwargs)

    def alert(self, data):
        #checking the number of the detector in the coincidence
        #print(list(data))
        #coinc_detector = list(data)[-3]
        #print('km3_data')
        #print(data['detector_names'])
        for coinc_detector in data['detector_names']:
            if coinc_detector == 'DS-20KnT':
                logging.info('FOUND DS-20K DATA')
                data['det_data'] = 'DS-20K'
                #### Add other conditions to veryfy the completness of the data

                return data
        return False




    ####Following might be useful if you want to run MC trials::
                #try:

                #    if 'neutrino_time' in data[coinc_detector]:
                #        keys_to_remove = ["gen", "neutrino_time", "sn_time"]
                #        for key in keys_to_remove:
                #            if key in data:
                #                del data[key]
                #        #newdata = data.copy()
                #        #newdata['coinc'] = data[coinc_detector]
                #        #print(list(data))
                #        data['coinc'] = data[coinc_detector]
                #        for key in list(data):
                #            if 'coinc' in key and key != 'coinc_id' and key !='number_of_coinc_dets' and key != 'coinc':
                #                #del newdata[key]
                #                del data[key]
                #        #data = newdata.copy()
                #        data['coinc']['detector_name'] = 'KM3'

                #        logging.info(data)
                #        return True
                #except:
                #    pass

