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
from define import define

bucket_name_informations = 'bucket-inf-notebook-informations'
bucket_name_details = 'bucket-inf-notebook-details'
bucket_name_musics = 'bucket-inf-notebook-musics'
service_account_info = service_account_info

object_name_musics = 'musics.json'

informations_dirname = 'informations'
details_dirname = 'details'

class StorageAccessor():
    client = None
    bucket_informations = None
    bucket_details = None
    bucket_musics = None
    blob_musics = None

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
    
    def connect_bucket_musics(self):
        if self.client is None:
            self.connect_client()
        if self.client is None:
            return
        
        try:
            self.bucket_musics = self.client.get_bucket(bucket_name_musics)
            logger.debug('connect bucket musics')
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

    def upload_collection(self, screen, result, force):
        self.connect_client()
        if self.client is None:
            return
        
        object_name = f'{uuid.uuid1()}.png'

        informations_trim = force
        details_trim = force

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
        
        if result.details.clear_type.best is None:
            details_trim = True
        if result.details.dj_level.best is None:
            details_trim = True
        if result.details.score.best is None:
            details_trim = True
        if result.details.clear_type.current is None:
            details_trim = True
        if result.details.dj_level.current is None:
            details_trim = True
        if result.details.score.current is None:
            details_trim = True

        if informations_trim:
            trim = screen.image.crop(define.informations_trimarea)
            Thread(target=self.upload_informations, args=(object_name, trim,)).start()

        if details_trim:
            play_side = result.play_side
            trim = screen.image.crop(define.details_trimarea[play_side])
            Thread(target=self.upload_details, args=(object_name, trim,)).start()
    
    def upload_resource_musics(self, filepath):
        if self.bucket_musics is None:
            self.connect_bucket_musics()
        if self.bucket_musics is None:
            return

        try:
            blob = self.bucket_musics.blob(object_name_musics)
            blob.upload_from_filename(filepath)
            logger.debug(f'upload resource musics')
        except Exception as ex:
            logger.exception(ex)
    
    def get_resource_musics_timestamp(self):
        if self.bucket_musics is None:
            self.connect_bucket_musics()
        if self.bucket_musics is None:
            return False

        try:
            self.blob_musics = self.bucket_musics.get_blob(object_name_musics)
            return self.blob_musics.updated
        except Exception as ex:
            logger.exception(ex)
        
        return None
    
    def download_resource_musics(self, filepath):
        if self.bucket_musics is None:
            self.connect_bucket_musics()
        if self.bucket_musics is None:
            return False
        
        if self.blob_musics is None:
            self.get_resource_musics_timestamp()
        if self.blob_musics is None:
            return False

        try:
            self.blob_musics.download_to_filename(filepath)
            logger.debug('download resource musics')
        except Exception as ex:
            logger.exception(ex)
            return False
        
        return True

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

        count = 0
        blobs = self.client.list_blobs(bucket_name_informations)
        for blob in blobs:
            self.save_image(informations_dirpath, blob)
            blob.delete()
            count += 1

        blobs = self.client.list_blobs(bucket_name_details)
        for blob in blobs:
            self.save_image(details_dirpath, blob)
            blob.delete()
            count += 1

        print(f'download cont: {count}')
