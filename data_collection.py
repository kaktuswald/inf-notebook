import os
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

collection_basepath = 'collection_data'

images_informations_basepath = os.path.join(collection_basepath, 'informations')
images_details_basepath = os.path.join(collection_basepath, 'details')
images_resultjudges_basepath = os.path.join(collection_basepath, 'resultjudges')
images_resulttimings_basepath = os.path.join(collection_basepath, 'resulttimings')
images_resultcombobreak_basepath = os.path.join(collection_basepath, 'resultcombobreak')
images_resultothers_basepath = os.path.join(collection_basepath, 'resultothers')
images_musicselect_basepath = os.path.join(collection_basepath, 'musicselect')

label_result_filepath = os.path.join(collection_basepath, 'label_result.json')
label_resultothers_filepath = os.path.join(collection_basepath, 'label_resultothers.json')
label_musicselect_filepath = os.path.join(collection_basepath, 'label_musicselect.json')
label_resultjudges_filepath = os.path.join(collection_basepath, 'label_resultjudges.json')
label_resulttimings_filepath = os.path.join(collection_basepath, 'label_resulttimings.json')
label_resultcombobreak_filepath = os.path.join(collection_basepath, 'label_resultcombobreak.json')
