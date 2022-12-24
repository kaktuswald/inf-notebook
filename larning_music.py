from PIL import Image
import json
import sys
import os
import numpy as np
from base64 import b64encode
from scipy.stats import mode

from resources import recog_music_backgrounds_basename,recog_music_filename
from recog import informations_areas,music_background_y_position,music_clean_threshold
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

    if not os.path.exists('larning_background'):
        os.mkdir('larning_background')
    
    images = {}
    for key in keys:
        filename = f'{key}.png'
        loadpath = os.path.join(dc.informations_basepath, filename)
        if os.path.isfile(loadpath):
            image = Image.open(loadpath)
            images[key] = image

    background_sources = {}
    for image in images.values():
        key = image.getpixel((0, music_background_y_position))
        if not key in background_sources.keys():
            background_sources[key] = []
        trim = image.crop(informations_areas['music'])
        np_value = np.array(trim)
        background_sources[key].append(np_value.flatten())
    
    backgrounds = {}
    for key in background_sources.keys():
        stacked = np.stack(background_sources[key])
        result, count = mode(stacked, axis=0, keepdims=True)
        reshaped = result.reshape((height, width))
        backgrounds[key] = reshaped

        basename = recog_music_backgrounds_basename.replace('.npz', '')
        np.save(f'{basename}-{key}', reshaped)

        image = Image.fromarray(reshaped)
        image.save(f'larning_background/{key}.png')

    print(f'background count: {len(background_sources.keys())}')

    trim_x_area = range(informations_areas['music'][0], informations_areas['music'][2])

    if not os.path.exists('larning_music'):
        os.mkdir('larning_music')

    map = {}
    for key, value in images.items():
        label = labels[key]
        if 'music' in label.keys() and label['music'] != '':
            background_key = value.getpixel((0, music_background_y_position))
            trim = value.crop(informations_areas['music'])
            np_value = np.array(trim)

            masked = np.where(np_value==backgrounds[background_key], 0, np_value)
            cleaned = np.where(masked<music_clean_threshold, 0, masked)

            escape_music_name = label['music'].replace('"', '')
            escape_music_name = escape_music_name.replace('/', '')
            escape_music_name = escape_music_name.replace(',', '')
            escape_music_name = escape_music_name.replace('\n', '')
            escape_music_name = escape_music_name.replace('?', '')
            escape_music_name = escape_music_name.replace('!', '')
            escape_music_name = escape_music_name.replace('*', '')
            escape_music_name = escape_music_name.replace(':', '')

            trim.save(f'larning_music/{escape_music_name}-{background_key}-trim.png')

            reverse_masked = np.where(masked==0, 255, masked)
            image = Image.fromarray(reverse_masked)
            image.save(f'larning_music/{escape_music_name}-{background_key}-masked.png')

            reverse_cleaned = np.where(cleaned==0, 255, cleaned)
            image = Image.fromarray(reverse_cleaned)
            image.save(f'larning_music/{escape_music_name}-{background_key}-cleaned.png')

            target = map
            list = []
            for index in range(width-1):
                np_trim = cleaned[:,index].astype(np.uint8)
                string = b64encode(np_trim).decode('utf-8')
                list.append(string)

                if not string in target.keys():
                    target[string] = {}
                target = target[string]
            
            np_trim = cleaned[:,-1].astype(np.uint8)
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
