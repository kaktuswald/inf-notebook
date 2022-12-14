from PIL import Image
import json
import sys
import os
import numpy as np

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

    keys = [*labels.keys()]
    print(f'key count: {len(keys)}')

    width = informations_areas['music'][2] - informations_areas['music'][0]
    height = informations_areas['music'][3] - informations_areas['music'][1]

    images = {}
    befores = {}
    for key in keys:
        label = labels[key]
        if 'music' in label.keys() and label['music'] != '' and 'clear_type' in label.keys():
            loadpath = os.path.join(dc.informations_basepath, f'{key}.png')
            before = None
            if os.path.isfile(loadpath):
                image = Image.open(loadpath)
                crop = image.crop(informations_areas['music'])
                np_value = np.array(crop)
                index = np_value[0,0]
                if not index in images:
                    images[index] = np.copy(np_value)
                else:
                    images[index] = np.where(np_value==befores[index],np_value,images[index])
                befores[index] = np_value
    
    print(len(images))
    for key, value in images.items():
        image = Image.fromarray(value)
        image.save(f'larning_music/{key}.png')
