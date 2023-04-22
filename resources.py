import os
import numpy as np
from winsound import SND_FILENAME,PlaySound
from logging import getLogger
from PIL import Image

logger_child_name = 'resources'

logger = getLogger().getChild(logger_child_name)
logger.debug(f'loaded resources.py')

from define import define
from mask import Mask

resources_dirname = 'resources'

masks_dirname = 'masks'
sounds_dirname = 'sounds'

masks_dirpath = os.path.join(resources_dirname, masks_dirname)
sounds_dirpath = os.path.join(resources_dirname, sounds_dirname)

recog_musics_filename = f'musics{define.music_recognition_vesion}.json'
recog_musics_filepath = os.path.join(resources_dirname, recog_musics_filename)
recog_musics_timestamp_filepath = os.path.join(resources_dirname, 'musics_timestamp.txt')

sound_find_filepath = os.path.join(sounds_dirpath, 'find.wav')
sound_result_filepath = os.path.join(sounds_dirpath, 'result.wav')

class MusicsTimestamp():
    def get_timestamp(self):
        if not os.path.exists(recog_musics_timestamp_filepath):
            return None
        with open(recog_musics_timestamp_filepath, 'r') as f:
            timestamp = f.read()

        return timestamp

    def write_timestamp(self, timestamp):
        with open(recog_musics_timestamp_filepath, 'w') as f:
            f.write(timestamp)

def play_sound_find():
    if os.path.exists(sound_find_filepath):
        PlaySound(sound_find_filepath, SND_FILENAME)

def play_sound_result():
    if os.path.exists(sound_result_filepath):
        PlaySound(sound_result_filepath, SND_FILENAME)

masks = {}
for filename in os.listdir(masks_dirpath):
    key = filename.split('.')[0]
    filepath = os.path.join(masks_dirpath, filename)
    masks[key] = Mask(key, np.load(filepath))
