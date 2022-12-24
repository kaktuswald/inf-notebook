import sys
import os
import numpy as np
from PIL import Image
from logging import getLogger

logger_child_name = 'resources'

logger = getLogger().getChild(logger_child_name)
logger.debug(f'loaded resources.py')

from define import define
from mask import Mask

resources_dirname = 'resources'

masks_dirname = 'masks'

recog_music_filename = os.path.join(resources_dirname, 'musics.json')

def is_embedded():
    return hasattr(sys, '_MEIPASS')

def create_resource_directory():
    if is_embedded():
        logger.error(f"Can't create resource directory.")
        return

    if not os.path.exists(resources_dirpath):
        os.mkdir(resources_dirpath)

if is_embedded():
    resources_dirpath = os.path.join(sys._MEIPASS, resources_dirname)
else:
    resources_dirpath = resources_dirname

masks_dirpath = os.path.join(resources_dirpath, masks_dirname)

logger.debug(f'resource basepath: {resources_dirpath}')

masks = {}
for filename in os.listdir(masks_dirpath):
    key = filename.split('.')[0]
    filepath = os.path.join(masks_dirpath, filename)
    masks[key] = Mask(key, np.load(filepath))

find_images = {}
for key in define.screen_areas.keys():
    find_images[key] = Image.fromarray(masks[key].value)
