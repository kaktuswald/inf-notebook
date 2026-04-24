import numpy as np
from winsound import SND_FILENAME,PlaySound
import pickle
import gzip
from os import rename,remove
from os.path import join,isfile,exists
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {__name__}')

from PIL import Image

from define import define

resources_dirname = 'resources'

sounds_dirname = 'sounds'
images_dirname = 'images'

sounds_dirpath = join(resources_dirname, sounds_dirname)
images_dirpath = join(resources_dirname, images_dirname)

sound_result_filepath = join(sounds_dirpath, 'result.wav')

images_stamp_filepath = join(images_dirpath, 'stamp.png')

class Resource():
    def __init__(self):
        self.load_resource_musictable()
        self.load_resource_screenrecognition()
        self.load_resource_informations()
        self.load_resource_details()
        self.load_resource_resultothers()
        self.load_resource_musicselect()
        self.load_resource_notesradar()
        self.load_resource_unofficialdifficulty()

        self.imagevalue_musictableinformation = None

        self.image_stamp = Image.open(images_stamp_filepath)
    
    def load_resource_musictable(self):
        resourcename = f'musictable{define.musictable_version}'
        
        self.musictable = load_resource_serialized(resourcename, True)

    def load_resource_screenrecognition(self):
        resourcename = f'screenrecognition{define.screenrecognition_version}'
        
        self.screenrecognition = load_resource_serialized(resourcename, True)

    def load_resource_informations(self):
        resourcename = f'informations{define.informations_recognition_version}'
        
        self.informations = load_resource_serialized(resourcename, True)

    def load_resource_details(self):
        resourcename = f'details{define.details_recognition_version}'
        
        self.details = load_resource_serialized(resourcename, True)

    def load_resource_resultothers(self):
        resourcename = f'resultothers{define.resultothers_recognition_version}'
        
        self.resultothers = load_resource_serialized(resourcename, True)

    def load_resource_musicselect(self):
        resourcename = f'musicselect{define.musicselect_recognition_version}'
        
        self.musicselect = load_resource_serialized(resourcename, True)
    
    def load_resource_notesradar(self):
        resourcename = f'notesradar{define.notesradar_version}'
        
        self.notesradar: dict[str, dict[str, list[dict[str, str | int]]]] = load_resource_serialized(resourcename, True)
    
    def load_resource_unofficialdifficulty(self):
        resourcename = f'unofficialdifficulty{define.unofficialdifficulty_version}'
        
        self.unofficialdifficulty: dict = load_resource_serialized(resourcename, True)

class ResourceTimestamp():
    def __init__(self, resourcename):
        self.resourcename = resourcename
        self.filepath = join(resources_dirname, f'{resourcename}.timestamp')
    
    def get_timestamp(self):
        if not exists(self.filepath):
            return None
        with open(self.filepath, 'r') as f:
            timestamp = f.read()

        return timestamp

    def write_timestamp(self, timestamp):
        logger.debug(f'save timestamp file {self.resourcename} {timestamp}')
        with open(self.filepath, 'w') as f:
            f.write(timestamp)

def play_sound_result():
    if exists(sound_result_filepath):
        PlaySound(sound_result_filepath, SND_FILENAME)

def load_resource_serialized(resourcename: str, compress: bool = False) -> dict | None:
    '''リソースファイルをロードする

    もし一時ファイルが存在したら前回のダウンロードが失敗していたということなので、
    対象のファイルを削除して一時ファイルを元に戻す。

    Args:
        resourcename(str): 対象のリソース名
        compress(bool): gzip圧縮されている
    Returns:
        dict or None: ロードされたリソースデータ
    '''
    filepath = join(resources_dirname, f'{resourcename}.res')
    filepath_tmp = join(resources_dirname, f'{resourcename}.res.tmp')

    if exists(filepath_tmp):
        if exists(filepath):
            remove(filepath)
        rename(filepath_tmp, filepath)
    
    if not isfile(filepath):
        return None
    
    if not compress:
        with open(filepath, 'rb') as f:
            value = pickle.load(f)
    else:
        with gzip.open(filepath, 'rb') as f:
            value = pickle.load(f)
    
    return value

def load_resource_numpy(resourcename):
    filepath = join(resources_dirname, f'{resourcename}.npy')
    return np.load(filepath)

def get_resource_filepath(filename):
    return join(resources_dirname, filename)

def download_latestresource(storage, filename) -> bool:
    '''最新のリソースファイルをダウンロードする

    ローカルファイルとGCS上のファイルのタイムスタンプを比較して異なればダウンロードを試みる。
    ダウンロード開始前に現在のファイルを一時ファイルとしてファイル名を変更する。
    ダウンロードに成功した場合は、一時ファイルを削除する。
    もしダウンロードに失敗した場合、一時ファイルに戻す。

    Args:
        storage(): 対象のストレージ
        filename(str): 対象のファイル名
    Returns:
        bool: リソースファイルが更新された
    '''
    latest_timestamp: str | None = storage.get_resource_timestamp(filename)
    if latest_timestamp is None:
        logger.debug(f'Not in storage {filename}')
        return False
    
    filepath = join(resources_dirname, filename)

    timestamp = ResourceTimestamp(filename)
    local_timestamp: str | None = None
    if exists(filepath):
        local_timestamp = timestamp.get_timestamp()

    if local_timestamp == latest_timestamp:
        logger.debug(f'Is latest {filename}')
        return False
    
    filepath_tmp = f'{filepath}.tmp'
    if exists(filepath):
        rename(filepath, filepath_tmp)

    if storage.download_resource(filename, filepath):
        logger.debug(f'Download successful {filename}')
        timestamp.write_timestamp(latest_timestamp)

        if exists(filepath_tmp):
            remove(filepath_tmp)

        return True
    else:
        logger.debug(f'Download failured {filename}')
        if exists(filepath):
            remove(filepath)
        
        rename(filepath_tmp, filepath)

        return False

resource = Resource()
