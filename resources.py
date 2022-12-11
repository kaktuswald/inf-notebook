import sys
import os
import json
import numpy as np
from PIL import Image
from logging import getLogger

logger_child_name = 'resources'

logger = getLogger().getChild(logger_child_name)
logger.debug(f'loaded resources.py')

from mask import Mask

resources_dirname = 'resources'

areas_filename = 'areas.json'

finds_dirname = 'finds'
masks_dirname = 'masks'

title = u'beatmaniaIIDX INFINITAS リザルト手帳'
icon_path = 'icon.ico'

def is_embedded():
    return hasattr(sys, '_MEIPASS')

def create_resource_directory():
    if is_embedded():
        logger.error(f"Can't create resource directory.")
        return

    if not os.path.exists(resources_dirpath):
        os.mkdir(resources_dirpath)

def save_areas():
    if is_embedded():
        logger.error(f"Can't save {areas_filepath}")
        return

    create_resource_directory()

    with open(areas_filepath, 'w') as f:
        json.dump(areas, f, indent=2)

def create_masks_directory():
    if not os.path.exists(masks_dirpath):
        os.mkdir(masks_dirpath)

def save_mask(key, value):
    np.save(os.path.join(masks_dirpath, key), value)

def save_find_image(key, image):
    if is_embedded():
        logger.error(f"Can't save find images.")
        return

    if not os.path.exists(finds_dirpath):
        os.mkdir(finds_dirpath)
    
    if not os.path.exists(finds_dirpath):
        os.mkdir(finds_dirpath)
    
    if not key in finds.keys():
        finds[key] = {'area': areas['find'][key]}
    finds[key]['image'] = image

    filepath = os.path.join(finds_dirpath, f'{key}.png')
    image.save(filepath)

if is_embedded():
    resources_dirpath = os.path.join(sys._MEIPASS, resources_dirname)
else:
    resources_dirpath = resources_dirname

areas_filepath = os.path.join(resources_dirpath, areas_filename)
finds_dirpath = os.path.join(resources_dirpath, finds_dirname)
masks_dirpath = os.path.join(resources_dirpath, masks_dirname)

logger.debug(f'resource basepath: {resources_dirpath}')

try:
    with open(areas_filepath) as file:
        areas = json.load(file)
except Exception as e:
    areas = None
    logger.exception(e)
    logger.exception(f'failed load: {areas_filepath}')

finds = {}
for filename in os.listdir(finds_dirpath):
    key = filename.split('.')[0]
    filepath = os.path.join(finds_dirpath, filename)
    finds[key] = {
        'area': areas['find'][key],
        'image': Image.open(filepath)
    }

masks = {}
for filename in os.listdir(masks_dirpath):
    key = filename.split('.')[0]
    filepath = os.path.join(masks_dirpath, filename)
    masks[key] = Mask(key, np.load(filepath))
