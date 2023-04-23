import numpy as np
import pickle
from os.path import join,exists,isfile
from PIL import Image

from define import define
from raw_image import raws_basepath
from larning import RawLabel,create_resource_directory
from resources import resources_dirname

filename = 'result_check.res'
filepath = join(resources_dirname, filename)
if exists(filepath):
    with open(filepath, 'rb') as f:
        table = pickle.load(f)
else:
    table = {}

reverse = True

if not reverse:
    key_position = define.result_check['key_position']
    areas = define.result_check['areas']
else:
    reverse_key_position = list(define.result_check['key_position'])
    reverse_key_position[0] = -reverse_key_position[0] - 1
    reverse_key_position[2] = -reverse_key_position[2] - 1
    key_position = tuple(reverse_key_position)

    areas = {}
    for key, area in define.result_check['areas'].items():
        reverse_area = list(define.result_check['areas'][key])
        reverse_area[0] = slice(-reverse_area[0].start-1, -reverse_area[0].stop-1)
        reverse_area[2] = -reverse_area[2] - 1
        areas[key] = tuple(reverse_area)

class RawData():
    def __init__(self, filename, np_value):
        self.filename = filename
        self.np_value = np_value

def get_is_savable_result(np_value):
    background_key = np_value[key_position]
    if not background_key in table.keys():
        return False

    for area_key, area in areas.items():
        if not np.array_equal(np_value[area], table[background_key][area_key]):
            return False
    
    return True

def load_raws():
    labels = RawLabel()

    filenames = [*labels.all()]

    raws = []
    for filename in filenames:
        filepath = join(raws_basepath, filename)
        if isfile(filepath):
            label = labels.get(filename)

            if not 'screen' in label.keys() or label['screen'] != 'result':
                continue
            if not 'cutin_mission' in label.keys() or label['cutin_mission']:
                continue
            if not 'cutin_bit' in label.keys() or label['cutin_bit']:
                continue

            if not reverse:
                np_value = np.array(Image.open(filepath))
            else:
                np_value = np.array(Image.open(filepath))[::-1,:,::-1]
            raws.append(RawData(filename, np_value))
    
    print(f"raw count: {len(raws)}")

    return raws

def larning_result_check(raws):
    report = {}
    table = {}
    for raw in raws:
        background_key = raw.np_value[key_position]
        if not background_key in table.keys():
            print(background_key, raw.filename)
            table[background_key] = {}
            report[background_key] = {'names': []}
            for area_key, area in areas.items():
                table[background_key][area_key] = raw.np_value[area]
                report[background_key][area_key] = []
        target = report[background_key]
        for area_key, area in areas.items():
            value = raw.np_value[area]
            if not value.tolist() in target[area_key]:
                target[area_key].append(value.tolist())
                if not raw.filename in target['names']:
                    target['names'].append(raw.filename)

    print('background count', len(report.keys()))
    print(sorted([*report.keys()]))

    background_count = define.result_check['background_count']
    if len(report.keys()) != background_count:
        print('Wrong background count')

    duplicate_target = None
    for key, value in report.items():
        counts = [len(value[area_key]) for area_key in value.keys() if area_key != 'names']
        print(key, counts)
        if np.any(np.array(counts) != 1):
            duplicate_target = key

    if duplicate_target is not None:
        print('duplicate', duplicate_target)
        for filename in report[duplicate_target]['names']:
            print(filename)

    with open(filepath, 'wb') as f:
        pickle.dump(table, f)
    
    return table

if __name__ == '__main__':
    create_resource_directory()

    raws = load_raws()

    table = larning_result_check(raws)
    