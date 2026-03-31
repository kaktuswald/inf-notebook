from os import mkdir
from os.path import join,exists,splitext
import io
from json import load,dump,loads,dumps
from uuid import uuid1
from datetime import datetime,timezone,timedelta
from threading import Thread
from queue import Queue
from typing import Callable,Any,Tuple
from logging import getLogger

from google.cloud import storage
from google.cloud.storage import Blob
from PIL import Image,ImageDraw

logger = getLogger().getChild('storage')
logger.debug('loaded storage.py')

from service_account_info import service_account_info
from define import define
from cloud_function import callfunction_eventdelete

bucket_name_informations = 'bucket-inf-notebook-informations'
bucket_name_details = 'bucket-inf-notebook-details'
bucket_name_resultothers = 'bucket-inf-notebook-resultothers'
bucket_name_musicselect = 'bucket-inf-notebook-musicselect'
bucket_name_notesradarvalue = 'bucket-inf-notebook-notesradarvalue'
bucket_name_resources = 'bucket-inf-notebook-resources2'
bucket_name_discordwebhooks = 'bucket-inf-notebook-discordwebhook2'

informations_dirname = 'informations'
details_dirname = 'details'
resultothers_dirname = 'resultothers'
musicselect_dirname = 'musicselect'

notesradarvalues_filename = 'notesradarvalues.json'

result_rivalname_fillbox = (
    (
        define.details_graphtarget_name_area[0],
        define.details_graphtarget_name_area[1]
    ),
    (
        define.details_graphtarget_name_area[2],
        define.details_graphtarget_name_area[3]
    ),
)

musicselect_rivals_fillbox = (
    (
        define.musicselect_rivals_name_area[0],
        define.musicselect_rivals_name_area[1],
    ),
    (
        define.musicselect_rivals_name_area[2],
        define.musicselect_rivals_name_area[3]
    ),
)

class StorageAccessor():
    class WorkerThread(Thread):
        queue: Queue[Tuple[Callable[..., Any], tuple, dict]] = Queue()

        def __init__(self):
            super().__init__(daemon=True)
        
        def run(self):
            while True:
                func, args, kwargs = self.queue.get()
                try:
                    func(*args, **kwargs)
                finally:
                    self.queue.task_done()
        
        def pushfunc(self, func: Callable[..., Any], *args, **kwargs):
            self.queue.put((func, args, kwargs,))

    client = None
    bucket_informations = None
    bucket_details = None
    bucket_resultothers = None
    bucket_musicselect = None
    bucket_notesradarvalue = None
    bucket_resources = None
    bucket_discordwebhooks = None
    blob_musics = None
    worker = WorkerThread()

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
    
    def connect_bucket_resultothers(self):
        if self.client is None:
            self.connect_client()
        if self.client is None:
            return
        
        try:
            self.bucket_resultothers = self.client.get_bucket(bucket_name_resultothers)
            logger.debug('connect bucket resultothers')
        except Exception as ex:
            logger.exception(ex)
    
    def connect_bucket_musicselect(self):
        if self.client is None:
            self.connect_client()
        if self.client is None:
            return
        
        try:
            self.bucket_musicselect = self.client.get_bucket(bucket_name_musicselect)
            logger.debug('connect bucket musicselect')
        except Exception as ex:
            logger.exception(ex)
    
    def connect_bucket_notesradarvalue(self):
        if self.client is None:
            self.connect_client()
        if self.client is None:
            return
        
        try:
            self.bucket_notesradarvalue = self.client.get_bucket(bucket_name_notesradarvalue)
            logger.debug('connect bucket notesradarvalue')
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

    def connect_bucket_discordwebhooks(self):
        if self.client is None:
            self.connect_client()
        if self.client is None:
            return
        
        try:
            self.bucket_discordwebhooks = self.client.get_bucket(bucket_name_discordwebhooks)
            logger.debug('connect bucket discordwebhooks')
        except Exception as ex:
            logger.exception(ex)

    def upload_image(self, blob, image):
        bytes = io.BytesIO()
        image.save(bytes, 'PNG')
        blob.upload_from_file(bytes, True)
        bytes.close()

    def upload_informations(self, object_name, image):
        if self.bucket_informations is None:
            self.connect_bucket_informations()
        if self.bucket_informations is None:
            return

        try:
            blob = self.bucket_informations.blob(object_name)
            self.upload_image(blob, image)
            logger.info(f'upload information image {object_name}')
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
            logger.info(f'upload details image {object_name}')
        except Exception as ex:
            logger.exception(ex)

    def upload_resultothers(self, object_name, image):
        if self.bucket_resultothers is None:
            self.connect_bucket_resultothers()
        if self.bucket_resultothers is None:
            return

        try:
            blob = self.bucket_resultothers.blob(object_name)
            self.upload_image(blob, image)
            logger.info(f'upload resultothers image {object_name}')
        except Exception as ex:
            logger.exception(ex)

    def upload_musicselect(self, object_name, image):
        if self.bucket_musicselect is None:
            self.connect_bucket_musicselect()
        if self.bucket_musicselect is None:
            return

        try:
            blob = self.bucket_musicselect.blob(object_name)
            self.upload_image(blob, image)
            logger.info(f'upload musicselect image {object_name}')
        except Exception as ex:
            logger.exception(ex)

    def upload_notesradarvalue(self, object_name, data):
        if self.bucket_notesradarvalue is None:
            self.connect_bucket_notesradarvalue()
        if self.bucket_notesradarvalue is None:
            return

        try:
            blob = self.bucket_notesradarvalue.blob(object_name)
            blob.upload_from_string(dumps(data))
            logger.info(f'upload notesradarvalue image {object_name}')
        except Exception as ex:
            logger.exception(ex)

    def start_uploadinformations(self, image: Image.Image):
        '''リザルト画面の譜面情報の収集画像をアップロードする

        Args:
            image (Image): 対象のリザルト画像(PIL.Image)
        '''
        self.connect_client()
        if self.client is None:
            return
        
        object_name = f'{uuid1()}.png'

        trim = image.crop(define.informations_trimarea)
        self.worker.pushfunc(self.upload_informations, object_name, trim)
        if not self.worker.is_alive():
            self.worker.start()
    
    def start_uploaddetails(self, image: Image.Image, playside: str):
        '''リザルト画面の詳細の収集画像をアップロードする

        Args:
            image (Image): 対象のリザルト画像(PIL.Image)
        '''
        if not playside:
            return
        
        self.connect_client()
        if self.client is None:
            return
        
        object_name = f'{uuid1()}.png'

        trim = image.crop(define.details_trimareas[playside])
        self.worker.pushfunc(self.upload_details, object_name, trim)
        if not self.worker.is_alive():
            self.worker.start()
    
    def start_uploadresultothers(self, image: Image.Image, playside: str):
        '''リザルト画面の詳細の反対側の収集画像をアップロードする

        Args:
            image (Image): 対象のリザルト画像(PIL.Image)
        '''
        if not playside:
            return
        
        self.connect_client()
        if self.client is None:
            return
        
        object_name = f'{uuid1()}.png'

        trim = image.crop(define.resultothers_trimareas[playside])
        self.worker.pushfunc(self.upload_resultothers, object_name, trim)
        if not self.worker.is_alive():
            self.worker.start()
    
    def start_uploadmusicselect(self, image: Image.Image):
        '''選曲画面の収集画像をアップロードする

        Args:
            image (Image): 対象のリザルト画像(PIL.Image)
        '''
        self.connect_client()
        if self.client is None:
            return
        
        object_name = f'{uuid1()}.png'

        trim = image.crop(define.musicselect_trimarea)
        image_draw = ImageDraw.Draw(trim)
        image_draw.rectangle(musicselect_rivals_fillbox, fill=0)
        self.worker.pushfunc(self.upload_musicselect, object_name, trim)
        if not self.worker.is_alive():
            self.worker.start()
    
    def start_uploadnotesradarvalue(self, data: dict):
        '''ノーツレーダー値をアップロードする

        Args:
            data (dict): ノーツレーダー値データ
        '''
        self.connect_client()
        if self.client is None:
            return
        
        object_name = f'{uuid1()}.json'

        self.worker.pushfunc(self.upload_notesradarvalue, object_name, data)
        if not self.worker.is_alive():
            self.worker.start()
    
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
            return None

        try:
            blob = self.bucket_resources.get_blob(resourcename)
            if blob is None:
                return None
            
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
            logger.info('download resource {targetfilepath}')
        except Exception as ex:
            logger.exception(ex)
            return False
        
        return True
    
    def download_discordwebhooks(self) -> dict[dict] | None:
        if self.bucket_discordwebhooks is None:
            self.connect_bucket_discordwebhooks()
        if self.bucket_discordwebhooks is None:
            return None
        
        list = {}

        blobs = self.client.list_blobs(bucket_name_discordwebhooks)
        deletetargets = []
        for blob in blobs:
            blob: Blob = blob
            try:
                content = loads(blob.download_as_string())
            except Exception as ex:
                continue

            if not 'enddatetime' in content.keys():
                continue

            enddt = datetime.strptime(content['enddatetime'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            nowdt = datetime.now(timezone.utc)

            if nowdt <= enddt + timedelta(weeks=1):
                list[splitext(blob.name)[0]] = content
            else:
                deletetargets.append(blob.name)
        
        if len(deletetargets):
            callfunction_eventdelete(deletetargets)
        
        return list

    def upload_discordwebhook(self, filename: str, value: dict) -> bool:
        '''
        イベント内容ファイルをアップロードする

        Args:
            filename(str): ファイル名
            value(dict): イベント内容
        Returns:
            bool: アップロードの成功
        '''
        if self.bucket_discordwebhooks is None:
            self.connect_bucket_discordwebhooks()
        if self.bucket_discordwebhooks is None:
            return False
        
        try:
            blob = self.bucket_discordwebhooks.blob(filename)
            blob.upload_from_string(dumps(value))
            logger.info(f'upload discordwebhooks {filename}')
        except Exception as ex:
            logger.exception(ex)
            return False

        return True
    
    def save_image(self, basepath, blob: Blob):
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
        resultothers_dirpath = join(basedir, resultothers_dirname)
        musicselect_dirpath = join(basedir, musicselect_dirname)

        notesradarvalues_filepath = join(basedir, notesradarvalues_filename)

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

        blobs = self.client.list_blobs(bucket_name_resultothers)
        for blob in blobs:
            self.save_image(resultothers_dirpath, blob)
            blob.delete()
            count += 1

        blobs = self.client.list_blobs(bucket_name_musicselect)
        for blob in blobs:
            self.save_image(musicselect_dirpath, blob)
            blob.delete()
            count += 1

        try:
            with open(notesradarvalues_filepath, 'r') as f:
                notesradarvalues = load(f)
        except Exception as ex:
            notesradarvalues = []
        
        blobs = self.client.list_blobs(bucket_name_notesradarvalue)
        for blob in blobs:
            notesradarvalues.append(loads(blob.download_as_text()))
            # self.save_image(musicselect_dirpath, blob)
            blob.delete()
            count += 1
        
        with open(notesradarvalues_filepath, 'w') as f:
            dump(notesradarvalues, f, indent=2)

        print(f'download count: {count}')
