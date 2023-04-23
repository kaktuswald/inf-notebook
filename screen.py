import numpy as np
import pickle
from os.path import join,exists,isfile
from PIL import Image

from define import define
from raw_image import raws_basepath
from larning import RawLabel,create_larningbase_dir,create_larning_dir,create_resource_directory,larningbase_direpath
from resources import resources_dirname

filename = 'screen.res'
filepath = join(resources_dirname, filename)

larning_dirname = 'screen'
larning_dirpath = join(larningbase_direpath, larning_dirname)

if exists(filepath):
    with open(filepath, 'rb') as f:
        table = pickle.load(f)
else:
    table = {}

screen_areas = define.screen_areas
screen_keys = [*screen_areas.keys()]

class RawData():
    def __init__(self, filename, np_value, label):
        self.filename = filename
        self.np_value = np_value
        self.label = label

def check_screen(screen, np_value):
    if not screen in screen_keys:
        return None
    
    return np.array_equal(np_value[screen_areas[screen]], table[screen])

def load_raws():
    raws = {}
    for screen in screen_keys:
        raws[screen] = {}
    raws['others'] = {}

    labels = RawLabel()

    filenames = [*labels.all()]

    count = 0
    for filename in filenames:
        filepath = join(raws_basepath, filename)
        if not isfile(filepath):
            continue

        label = labels.get(filename)
        if not 'screen' in label.keys():
            continue

        if label['screen'] in screen_keys:
            screen = label['screen']
        else:
            screen = 'others'

        raws[screen][filename] = np.array(Image.open(filepath))
        count += 1
    
    print(f"raw count: {count}")

    return raws

def larning_and_check_screen(raws):
    create_larningbase_dir()
    create_larning_dir(larning_dirpath)

    table = {}
    wrong_count = 0
    for screen in screen_keys:
        table[screen] = [*raws[screen].values()][0][screen_areas[screen]]
        image = Image.fromarray(table[screen])
        image.save(join(larning_dirpath, f'{screen}.png'))

        print(screen, len(raws[screen]))
        for key, value in raws[screen].items():
            np_value = value[screen_areas[screen]]
            if not np.array_equal(np_value, table[screen]):
                print('NG', screen, key)
                wrong_count += 1
                Image.fromarray(np_value).save(join(larning_dirpath, key))
    
    check_count = 0
    for screen1 in raws.keys():
        for key, value in raws[screen1].items():
            for screen2 in screen_keys:
                if screen1 != screen2:
                    check_count += 1
                    if np.array_equal(value[screen_areas[screen2]], table[screen2]):
                        print('NG', screen1, screen2, key)
                        wrong_count += 1
    print('check count', check_count)
    
    if wrong_count != 0:
        print(wrong_count)
        return None
    
    for key, value in table.items():
        table[key] = value[::-1, :]
        
    with open(filepath, 'wb') as f:
        pickle.dump(table, f)
    
    return table

if __name__ == '__main__':
    create_resource_directory()

    raws = load_raws()

    table = larning_and_check_screen(raws)
    