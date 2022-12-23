from PIL import Image
import os
import numpy as np
import shutil
from logging import getLogger
import json

logger_child_name = 'larning'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded larning.py')

from raw_image import raws_basepath
from resources import masks_dirpath,create_resource_directory

larningbase_direpath = 'larning'
mask_images_dirpath = os.path.join(larningbase_direpath, 'mask_images')

label_basics_filepath = os.path.join(raws_basepath, 'label.json')
label_collections_filepath = os.path.join(raws_basepath, 'label.json')

class RawLabel:
    labels = {}

    def __init__(self):
        self.load()

    def load(self):
        try:
            with open(label_basics_filepath) as f:
                self.labels = json.load(f)
        except Exception:
            self.labels = {}

    def save(self):
        with open(label_basics_filepath, 'w') as f:
            json.dump(self.labels, f, indent=2)

    def get(self, filename):
        if filename in self.labels:
            return self.labels[filename]
        
        return None
    
    def all(self):
        return self.labels.keys()

    def remove(self, filename):
        if filename in self.labels:
            del self.labels[filename]

    def update(self, filename, values):
        self.labels[filename] = values

class LarningSource():
    def __init__(self, filename, image, label):
        self.filename = filename
        self.image = image
        self.label = label

def create_masks_directory():
    create_resource_directory()

    if not os.path.exists(masks_dirpath):
        os.mkdir(masks_dirpath)

def save_mask(key, value):
    create_masks_directory()
    np.save(os.path.join(masks_dirpath, key), value)

def save_raw(screen):
    if not os.path.exists(raws_basepath):
        os.mkdir(raws_basepath)

    filepath = os.path.join(raws_basepath, screen.filename)
    if not os.path.exists(filepath):
        screen.original.save(filepath)

def load_larning_sources():
    labels = RawLabel()

    filenames = [*labels.all()]
    print(f"label count: {len(filenames)}")

    sources = []
    for filename in filenames:
        filepath = os.path.join(raws_basepath, filename)
        if os.path.isfile(filepath):
            image = Image.open(filepath).convert('L')
            sources.append(LarningSource(filename, image, labels.get(filename)))
    
    return sources

def larning(key, targets):
    if len(targets) == 0:
        return

    pattern_count = 0
    patterns = []

    if not os.path.exists(larningbase_direpath):
        os.mkdir(larningbase_direpath)

    larning_dirpath = os.path.join(larningbase_direpath, key)
    if os.path.exists(larning_dirpath):
        try:
            shutil.rmtree(larning_dirpath)
        except Exception as ex:
            print(ex)

    if not os.path.exists(larning_dirpath):
        os.mkdir(larning_dirpath)

    for target in targets.items():
        if not target[1] in patterns:
            patterns.append(target[1])
            pattern_count += 1
            filepath = os.path.join(larning_dirpath, f"{pattern_count}-{target[0]}")
            target[1].save(filepath)
    
    np_targets = [np.array(target) for target in targets.values()]

    mask = np.copy(np_targets[0])
    for target in np_targets[1:]:
        mask = np.where(mask|mask==target, mask, 0)

    save_mask(key, mask)

    mask_image = Image.fromarray(mask)

    larning_filepath = os.path.join(larning_dirpath, f"{key}.png")
    mask_image.save(larning_filepath)

    if not os.path.exists(mask_images_dirpath):
        os.mkdir(mask_images_dirpath)

    mask_image_filepath = os.path.join(mask_images_dirpath, f"{key}.png")
    mask_image.save(mask_image_filepath)

    print(f"[{key}]source count: {len(targets)} / pattern count: {len(patterns)}")

    return mask

def is_result_ok(label):
    if not label['trigger']:
        return False
    
    if label['cutin_mission']:
        return False
    if label['cutin_bit']:
        return False
    
    if label['play_side'] == '':
        return False
    
    return True
