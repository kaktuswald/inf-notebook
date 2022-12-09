import os
import io
from google.cloud import storage
import uuid
from PIL import Image

from threading import Thread
from logging import getLogger

logger = getLogger().getChild('uploader')
logger.debug('loaded uploader.py')

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
        
        self.bucket_informations = self.client.bucket(bucket_name_informations)
        logger.debug('connect bucket informations')

    def connect_bucket_details(self):
        if self.client is None:
            self.connect_client()
        if self.client is None:
            return
        
        self.bucket_details = self.client.bucket(bucket_name_details)
        logger.debug('connect bucket details')

    def upload_image(self, blob, image):
        bytes = io.BytesIO()
        image.save(bytes, 'PNG')
        blob.upload_from_file(bytes, True)

    def upload_informations(self, object_name, image):
        if self.bucket_informations is None:
            self.connect_bucket_informations()
        if self.bucket_informations is None:
            return

        blob = self.bucket_informations.blob(object_name)
        self.upload_image(blob, image)
        logger.debug(f'upload information image {object_name}')

    def upload_details(self, object_name, image):
        if self.bucket_details is None:
            self.connect_bucket_details()
        if self.bucket_details is None:
            return

        blob = self.bucket_details.blob(object_name)
        self.upload_image(blob, image)
        logger.debug(f'upload details image {object_name}')

    def upload_collection(self, screen, result):
        object_name = f'{uuid.uuid1()}.png'

        informations_trim = True

        if informations_trim:
            trim = screen.image.crop(informations_trimarea)
            Thread(target=self.upload_informations, args=(object_name, trim,)).start()

        details_trim = False
        details = result.details
        if details['use_option']:
            details_trim = True
        
        for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
            if details[key] is None:
                details_trim = True
        if details['clear_type'] == 'F-COMBO':
            details_trim = True

        details_trim = True
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
