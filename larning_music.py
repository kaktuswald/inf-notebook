from PIL import Image
import json
import sys
import os
import numpy as np
from base64 import b64encode

from resources import recog_music_filename
from recog import Recognition,music_block_size,informations_areas,music_color_define
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
    x_count = int(width / music_block_size)
    y_count = int(height / music_block_size)
    blocks = []
    for x in range(x_count):
        for y in range(y_count):
            x_p = int(x_count / 2 - (int(x / 2) + 1) if x % 2 else x_count /2 + int(x / 2))
            blocks.append([
                x_p * music_block_size,
                y * music_block_size,
                (x_p + 1) * music_block_size,
                (y + 1) * music_block_size
            ])
    print('block count: ', len(blocks))

    mask = np.zeros((height, width), dtype=np.uint8)
    for i in range(len(music_color_define)):
        mask[i,:] = music_color_define[i]
    map = {}
    for key in keys:
        label = labels[key]
        if 'music' in label.keys() and label['music'] != '' and 'clear_type' in label.keys() and label['clear_type'] == 'FAILED':
            filename = f'{key}.png'
            loadpath = os.path.join(dc.informations_basepath, filename)
            music_name = labels[key]['music']
            escape_music_name = music_name.replace('"', '')
            if os.path.isfile(loadpath):
                image = Image.open(loadpath)
                crop = image.crop(informations_areas['music'])
                np_value = np.array(crop)
                result = np.where(np_value==mask,mask, 0)
                target = map
                for block in blocks:
                    np_trim = result[block[1]:block[3],block[0]:block[2]].astype(np.uint8)
                    string = b64encode(np_trim).decode('utf-8')
                    if not string in target:
                        target[string] = {}
                    target = target[string]
                block = blocks[-1]
                np_trim = result[block[1]:block[3],block[0]:block[2]].astype(np.uint8)
                string = b64encode(np_trim).decode('utf-8')
                target[string] = music_name

    with open(recog_music_filename, 'w') as f:
        json.dump(map, f)
