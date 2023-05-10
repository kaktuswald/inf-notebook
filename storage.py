from os import mkdir
from os.path import join,exists
import io
from google.cloud import storage
import uuid
from PIL import Image,ImageDraw

from threading import Thread
from logging import getLogger

logger = getLogger().getChild('storage')
logger.debug('loaded storage.py')

from service_account_info import service_account_info
from define import define

bucket_name_informations = 'bucket-inf-notebook-informations'
bucket_name_details = 'bucket-inf-notebook-details'
bucket_name_musics = 'bucket-inf-notebook-musics'
bucket_name_resources = 'bucket-inf-notebook-resources'

service_account_info = service_account_info

informations_dirname = 'informations'
details_dirname = 'details'

rivalname_fillbox = (
    (
        define.details_areas['graphtarget']['name'][0],
        define.details_areas['graphtarget']['name'][1]
    ),
    (
        define.details_areas['graphtarget']['name'][2],
        define.details_areas['graphtarget']['name'][3]
    )
)

class StorageAccessor():
    client = None
    bucket_informations = None
    bucket_details = None
    bucket_musics = None
    bucket_resources = None
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
    
    def connect_bucket_resources(self):
        if self.client is None:
            self.connect_client()
        if self.client is None:
            return
        
        try:
            self.bucket_resources = self.client.get_bucket(bucket_name_resources)
            logger.debug('connect bucket resources')
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

    def upload_collection(self, result, force):
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
        
        if not result.details.options.special:
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

        if result.details.graphtarget is None:
            details_trim = True

        if informations_trim:
            trim = result.image.crop(define.informations_trimarea_new)
            Thread(target=self.upload_informations, args=(object_name, trim,)).start()
        if details_trim:
            play_side = result.play_side
            trim = result.image.crop(define.details_trimarea[play_side])
            image_draw = ImageDraw.Draw(trim)
            image_draw.rectangle(rivalname_fillbox, fill=0)
            Thread(target=self.upload_details, args=(object_name, trim,)).start()
    
    def upload_resource(self, resourcename, targetfilepath):
        if self.bucket_resources is None:
            self.connect_bucket_resources()
        if self.bucket_resources is None:
            return

        try:
            blob = self.bucket_resources.blob(resourcename)
            blob.upload_from_filename(targetfilepath)
            logger.debug(f'upload resource {targetfilepath}')
        except Exception as ex:
            logger.exception(ex)
    
    def get_resource_timestamp(self, resourcename):
        if self.bucket_resources is None:
            self.connect_bucket_resources()
        if self.bucket_resources is None:
            return False

        try:
            blob = self.bucket_resources.get_blob(resourcename)
            return str(blob.updated)
        except Exception as ex:
            logger.exception(ex)
        
        return None
    
    def download_resource(self, resourcename, targetfilepath):
        if self.bucket_resources is None:
            self.connect_bucket_resources()
        if self.bucket_resources is None:
            return False
        
        blob = self.bucket_resources.get_blob(resourcename)

        try:
            blob.download_to_filename(targetfilepath)
            logger.debug('download resource {targetfilepath}')
        except Exception as ex:
            logger.exception(ex)
            return False
        
        return True

    def save_image(self, basepath, blob):
        if not exists(basepath):
            mkdir(basepath)
        
        image_bytes = blob.download_as_bytes()
        image = Image.open(io.BytesIO(image_bytes))
        filepath = join(basepath, blob.name)
        image.save(filepath)

    def download_and_delete_all(self, basedir):
        self.connect_client()
        if self.client is None:
            print('connect client failed')
            return

        if not exists(basedir):
            mkdir(basedir)

        informations_dirpath = join(basedir, informations_dirname)
        details_dirpath = join(basedir, details_dirname)

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
