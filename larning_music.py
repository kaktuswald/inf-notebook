from PIL import Image
import json
import sys
import os
import numpy as np

from resources import recog_musics_filepath
from define import define
import data_collection as dc

if __name__ == '__main__':
    if not os.path.isfile(dc.label_filepath):
        print(f"{dc.label_filepath}が見つかりませんでした。")
        sys.exit()

    try:
        with open(dc.label_filepath) as f:
            labels = json.load(f)
    except Exception:
        print(f"{dc.label_filepath}を読み込めませんでした。")
        sys.exit()

    output = []

    keys = [*labels.keys()]
    print(f"file count: {len(keys)}")

    width = define.informations_areas['music'][2] - define.informations_areas['music'][0]
    height = define.informations_areas['music'][3] - define.informations_areas['music'][1]

    images = {}
    for key in keys:
        filename = f'{key}.png'
        loadpath = os.path.join(dc.informations_basepath, filename)
        if os.path.isfile(loadpath):
            image = Image.open(loadpath)
            images[key] = image

    if not os.path.exists('larning_music'):
        os.mkdir('larning_music')

    map = {}
    for key, value in images.items():
        label = labels[key]
        if label['informations'] is not None and label['informations']['music'] != '':
            trim = value.crop(define.informations_areas['music'])
            np_value = np.array(trim)
            summed = np.sum(np_value, axis=1)

            escape_music_name = label['informations']['music'].replace('"', '')
            escape_music_name = escape_music_name.replace('/', '')
            escape_music_name = escape_music_name.replace(',', '')
            escape_music_name = escape_music_name.replace('\n', '')
            escape_music_name = escape_music_name.replace('?', '')
            escape_music_name = escape_music_name.replace('!', '')
            escape_music_name = escape_music_name.replace('*', '')
            escape_music_name = escape_music_name.replace(':', '')

            trim.save(f'larning_music/{escape_music_name}-{key}.png')

            target = map
            list = []
            for index in range(len(summed)-1):
                value = str(summed[index])
                if not value in target.keys():
                    target[value] = {}
                target = target[value]
            
            value = str(summed[-1])
            list.append(value)
            if value in target.keys() and target[value] != label['informations']['music']:
                print('Failure')
                print(target[value], label['informations']['music'], filename)
                print(list)
                sys.exit()

            target[value] = label['informations']['music']

    with open(recog_musics_filepath, 'w') as f:
        json.dump(map, f)
