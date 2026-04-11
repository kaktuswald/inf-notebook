import os
from logging import getLogger

logger = getLogger(__name__)
logger.debug(f'loaded {__name__}')

collection_basepath = 'collection_data'

images_informations_basepath = os.path.join(collection_basepath, 'informations')
images_details_basepath = os.path.join(collection_basepath, 'details')
images_resultothers_basepath = os.path.join(collection_basepath, 'resultothers')
images_musicselect_basepath = os.path.join(collection_basepath, 'musicselect')

label_result_filepath = os.path.join(collection_basepath, 'label_result.json')
label_resultothers_filepath = os.path.join(collection_basepath, 'label_resultothers.json')
label_musicselect_filepath = os.path.join(collection_basepath, 'label_musicselect.json')
