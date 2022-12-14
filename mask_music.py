from PIL import Image
import json
import sys
import os
import numpy as np

from recog import informations_areas,music_color_define
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

    keys = [*labels.keys()]

    width = informations_areas['music'][2] - informations_areas['music'][0]
    height = informations_areas['music'][3] - informations_areas['music'][1]

    mask = np.zeros((height, width), dtype=np.uint8)
    for i in range(len(music_color_define)):
        mask[i,:] = music_color_define[i]
    for key in keys:
        label = labels[key]
        if 'music' in label.keys() and label['music'] != '' and 'clear_type' in label.keys() and label['clear_type'] != 'FAILED':
            loadpath = os.path.join(dc.informations_basepath, f'{key}.png')
            music_name = labels[key]['music']
            escape_music_name = music_name.replace('"', '')
            if os.path.isfile(loadpath):
                image = Image.open(loadpath)
                crop = image.crop(informations_areas['music'])
                np_value = np.array(crop)
                result = np.where(np_value==mask,mask, 0)
                result_image = Image.fromarray(result)
                result_image.save(f'larning_music/{escape_music_name}.png')
