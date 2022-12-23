from PIL import Image
import json
import sys
import os
import numpy as np
from base64 import b64encode

from resources import recog_music_filename
from recog import Recognition,informations_areas,music_trim_positions
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

    recog = Recognition()

    output = []

    keys = [*labels.keys()]
    print(f"file count: {len(keys)}")

    width = informations_areas['music'][2] - informations_areas['music'][0]
    height = informations_areas['music'][3] - informations_areas['music'][1]

    map = {}
    for key in keys:
        label = labels[key]
        if 'music' in label.keys() and label['music'] != '':
            filename = f'{key}.png'
            loadpath = os.path.join(dc.informations_basepath, filename)
            music_name = labels[key]['music']
            escape_music_name = music_name.replace('"', '')
            if os.path.isfile(loadpath):
                image = Image.open(loadpath)
                crop = image.crop(informations_areas['music'])
                np_value = np.array(crop)

                escape_name = music_name.replace('"', '')
                escape_name = escape_name.replace('/', '')
                escape_name = escape_name.replace(',', '')

                target = map
                list = []
                for index in range(len(music_trim_positions)-1):
                    position = music_trim_positions[index]

                    np_trim = np_value[:,position].astype(np.uint8)
                    string = b64encode(np_trim).decode('utf-8')
                    list.append(string)

                    if not string in target.keys():
                        target[string] = {}
                    target = target[string]
                
                np_trim = np_value[:,music_trim_positions[-1]].astype(np.uint8)
                string = b64encode(np_trim).decode('utf-8')
                list.append(string)
                if string in target.keys() and target[string] != music_name:
                    print('Failure')
                    print(target[string], music_name, filename)
                    print(list)
                    sys.exit()

                target[string] = music_name

    with open(recog_music_filename, 'w') as f:
        json.dump(map, f)
