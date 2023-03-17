from PIL import Image
import json
from sys import exit
from os import mkdir
from os.path import join,isfile,exists,basename
import numpy as np
import time

from define import define
import data_collection as dc

dirname = 'larning_music'

if not exists(dirname):
    mkdir(dirname)

background_basepath = join(dirname, 'backgrounds')
music_inspection_basepath = join(dirname, 'inspection')

arcadeallmusics_filename = 'musics_arcade_all.txt'
infinitasonlymusics_filename = 'musics_infinitas_only.txt'
registred_musics_filename = 'musics_registred.txt'
missing_musics_filename = 'musics_missing_in_arcade.txt'

area = define.informations_areas['music']
width = area[2] - area[0]
height = area[3] - area[1]
shape = (height, width)

target_background_key = 213
target_pos = (86, 6)
target_value = 198

class InformationsImage():
    def __init__(self, filepath, music):
        image = Image.open(filepath)
        self.background_key = image.getpixel(define.music_background_key_position)
        np_value = np.array(image)
        self.np_value = np_value[area[1]:area[3], area[0]:area[2]]
        self.music = music
        self.key = basename(filepath)

def load_images(keys, labels):
    images = {}
    for key in keys:
        filename = f'{key}.png'
        filepath = join(dc.informations_basepath, filename)
        if isfile(filepath):
            images[key] = InformationsImage(filepath, labels[key]['informations']['music'])
    
    return images

if __name__ == '__main__':
    if not isfile(dc.label_filepath):
        print(f"{dc.label_filepath}が見つかりませんでした。")
        exit()

    try:
        with open(dc.label_filepath) as f:
            labels = json.load(f)
    except Exception:
        print(f"{dc.label_filepath}を読み込めませんでした。")
        exit()

    keys = [key for key in labels.keys() if labels[key]['informations'] is not None and labels[key]['informations']['music'] != '']
    print(f"file count: {len(keys)}")

    images = load_images(keys, labels)

    filtered_images = []
    for image in images.values():
        if image.background_key != target_background_key:
            continue
        filtered_images.append(image)

    target_images = []
    patterns = {}
    for image in filtered_images:
        v = image.np_value[target_pos[1],target_pos[0]]
        if not v in patterns.keys():
            patterns[v] = []
        patterns[v].append(image)
        target_images.append(image)
    
    for key, value in patterns.items():
        print(key, len(value))
    
    print(target_value)
    for image in patterns[target_value]:
        print(image.key)
