import os
import io
from google.cloud import storage
import uuid
from PIL import Image

from threading import Thread
from logging import getLogger

logger = getLogger().getChild('storage')
logger.debug('loaded storage.py')

from service_account_info import service_account_info
from recog import informations_trimarea,details_trimarea

bucket_name_informations = 'bucket-infinitas-memorise-informations'
bucket_name_details = 'bucket-infinitas-memorise-details'
service_account_info = service_account_info

informations_dirname = 'informations'
details_dirname = 'details'

class StorageAccessor():
    client = None
    bucket_informations = None
    bucket_details = None

    def connect_client(self):
        if self.client is not None:
            return
        
        if service_account_info is None:
            logger.info('no define service_account_info')
            return
        
        self.client = storage.Client.from_service_account_info(service_account_info)
        logger.debug('connect client')

    def connect_bucket_informations(self):
        if self.client is None:
            self.connect_client()
        if self.client is None:
            return
        
        try:
            self.bucket_informations = self.client.get_bucket(bucket_name_informations)
            logger.debug('connect bucket informations')
        except Exception as ex:
            logger.exception(ex)

    def connect_bucket_details(self):
        if self.client is None:
            self.connect_client()
        if self.client is None:
            return
        
        try:
            self.bucket_details = self.client.get_bucket(bucket_name_details)
            logger.debug('connect bucket details')
        except Exception as ex:
            logger.exception(ex)

    def upload_image(self, blob, image):
        bytes = io.BytesIO()
        image.save(bytes, 'PNG')
        blob.upload_from_file(bytes, True)

    def upload_informations(self, object_name, image):
        if self.bucket_informations is None:
            self.connect_bucket_informations()
        if self.bucket_informations is None:
            return

        try:
            blob = self.bucket_informations.blob(object_name)
            self.upload_image(blob, image)
            logger.debug(f'upload information image {object_name}')
        except Exception as ex:
            logger.exception(ex)

    def upload_details(self, object_name, image):
        if self.bucket_details is None:
            self.connect_bucket_details()
        if self.bucket_details is None:
            return

        try:
            blob = self.bucket_details.blob(object_name)
            self.upload_image(blob, image)
            logger.debug(f'upload details image {object_name}')
        except Exception as ex:
            logger.exception(ex)

    def upload_collection(self, screen, result):
        self.connect_client()
        if self.client is None:
            return
        
        object_name = f'{uuid.uuid1()}.png'

        informations_trim = False
        details_trim = False

        if result.informations.play_mode is None:
            informations_trim = True
        if result.informations.difficulty is None:
            informations_trim = True
        if result.informations.level is None:
            informations_trim = True
        if result.informations.music is None:
            informations_trim = True

        if result.informations.play_mode == 'DP':
            details_trim = True
        if result.details.clear_type.value is None:
            details_trim = True
        if result.details.clear_type.value == 'F-COMBO':
            details_trim = True
        if result.details.dj_level.value is None:
            details_trim = True

        if informations_trim:
            trim = screen.image.crop(informations_trimarea)
            Thread(target=self.upload_informations, args=(object_name, trim,)).start()

        if details_trim:
            play_side = result.play_side
            trim = screen.image.crop(details_trimarea[play_side])
            Thread(target=self.upload_details, args=(object_name, trim,)).start()

    def save_image(self, basepath, blob):
        if not os.path.exists(basepath):
            os.mkdir(basepath)
        
        image_bytes = blob.download_as_bytes()
        image = Image.open(io.BytesIO(image_bytes))
        filepath = os.path.join(basepath, blob.name)
        image.save(filepath)

    def download_and_delete_all(self, basedir):
        self.connect_client()
        if self.client is None:
            print('connect client failed')
            return

        if not os.path.exists(basedir):
            os.mkdir(basedir)

        informations_dirpath = os.path.join(basedir, informations_dirname)
        details_dirpath = os.path.join(basedir, details_dirname)

        blobs = self.client.list_blobs(bucket_name_informations)
        for blob in blobs:
            self.save_image(informations_dirpath, blob)
            blob.delete()

        blobs = self.client.list_blobs(bucket_name_details)
        for blob in blobs:
            self.save_image(details_dirpath, blob)
            blob.delete()

        print('complete')
