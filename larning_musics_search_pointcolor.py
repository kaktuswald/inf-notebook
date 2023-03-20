from PIL import Image
import json
from sys import exit,argv
from os.path import join,isfile,basename
import numpy as np

from define import define
import data_collection as dc

if len(argv) == 1:
    print('please argment.')
    exit()

if not '-key' in argv or argv.index('-key') == len(argv) - 1 or not str.isdigit(argv[argv.index('-key') + 1]):
    print('please specify argment background key as "-key".')
    exit()

if not '-x' in argv or argv.index('-x') == len(argv) - 1 or not str.isdigit(argv[argv.index('-x') + 1]):
    print('please specify argment x position as "-x".')
    exit()

if not '-y' in argv or argv.index('-y') == len(argv) - 1 or not str.isdigit(argv[argv.index('-y') + 1]):
    print('please specify argment y position as "-y".')
    exit()

if not '-value' in argv or argv.index('-value') == len(argv) - 1 or not str.isdigit(argv[argv.index('-value') + 1]):
    print('please specify argment pixel value "-value".')
    exit()

target_background_key = int(argv[argv.index('-key') + 1])
target_pos = (int(argv[argv.index('-x') + 1]), int(argv[argv.index('-y') + 1]))
target_value = int(argv[argv.index('-value') + 1])

arcadeallmusics_filename = 'musics_arcade_all.txt'
infinitasonlymusics_filename = 'musics_infinitas_only.txt'
registred_musics_filename = 'musics_registred.txt'
missing_musics_filename = 'musics_missing_in_arcade.txt'

area = define.informations_areas['music']
width = area[2] - area[0]
height = area[3] - area[1]
shape = (height, width)

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
    
    if target_value in patterns.keys():
        for image in patterns[target_value]:
            print(image.key)
