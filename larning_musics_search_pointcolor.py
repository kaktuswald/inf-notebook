import json
from sys import exit,argv
from os.path import isfile

import data_collection as dc
from larning_musics import load_images

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

    filtered_images = {}
    for key, image in images.items():
        if image.background_key != target_background_key:
            continue
        filtered_images[key] = image

    patterns = {}
    for key, image in filtered_images.items():
        v = image.np_value[target_pos[1],target_pos[0]]
        if not v in patterns.keys():
            patterns[v] = []
        patterns[v].append(key)
    
    for key, value in patterns.items():
        print(key, len(value))
    
    if target_value in patterns.keys():
        for key in patterns[target_value]:
            print(key)
