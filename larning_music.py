from PIL import Image
import json
import sys
import os
import numpy as np
from base64 import b64encode
from scipy.stats import mode

from resources import recog_music_filename
from recog import informations_areas
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

    width = informations_areas['music'][2] - informations_areas['music'][0]
    height = informations_areas['music'][3] - informations_areas['music'][1]

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
        if 'music' in label.keys() and label['music'] != '':
            trim = value.crop(informations_areas['music'])
            np_value = np.array(trim)

            escape_music_name = label['music'].replace('"', '')
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
            for index in range(width-1):
                np_trim = np_value[:,index].astype(np.uint8)
                string = b64encode(np_trim).decode('utf-8')
                list.append(string)

                if not string in target.keys():
                    target[string] = {}
                target = target[string]
            
            np_trim = np_value[:,-1].astype(np.uint8)
            string = b64encode(np_trim).decode('utf-8')
            list.append(string)
            if string in target.keys() and target[string] != label['music']:
                print('Failure')
                print(target[string], label['music'], filename)
                print(list)
                sys.exit()

            target[string] = label['music']

    with open(recog_music_filename, 'w') as f:
        json.dump(map, f)
