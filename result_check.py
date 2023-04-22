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

background_count = define.result_check['background_count']
key_position = define.result_check['key_position']
areas = define.result_check['areas']

class RawData():
    def __init__(self, filename, np_value, label):
        self.filename = filename
        self.np_value = np_value
        self.label = label

def get_is_result_savable(np_value):
    key = np_value[key_position]
    if not key in table.keys():
        return None

    for area in areas:
        if not np.array_equal(np_value[area], table[key][str(area)]):
            return None
    
    return True

def load_raws():
    labels = RawLabel()

    filenames = [*labels.all()]

    raws = []
    for filename in filenames:
        filepath = join(raws_basepath, filename)
        if isfile(filepath):
            raws.append(RawData(filename, np.array(Image.open(filepath)), labels.get(filename)))
    
    print(f"raw count: {len(raws)}")

    return raws

def larning_result_check(raws):
    report = {}
    table = {}
    for raw in raws:
        if not 'screen' in raw.label.keys() or raw.label['screen'] != 'result':
            continue
        if not 'cutin_mission' in raw.label.keys() or raw.label['cutin_mission']:
            continue
        if not 'cutin_bit' in raw.label.keys() or raw.label['cutin_bit']:
            continue
        
        key = raw.np_value[key_position]
        if not key in table.keys():
            table[key] = {}
            report[key] = {'names': []}
            for area in areas:
                report[key][str(area)] = []
        target = report[key]
        for area in areas:
            area_key = str(area)
            value = raw.np_value[area]
            table[key][area_key] = value
            if not value.tolist() in target[area_key]:
                target[area_key].append(value.tolist())
                if not raw.filename in report[key]['names']:
                    report[key]['names'].append(raw.filename)

    print('background count', len(report.keys()))
    print(sorted([*report.keys()]))

    if len(report.keys()) != background_count:
        print('Wrong background count')

    duplicate_target = None
    for key, value in report.items():
        counts = [len(value[area_key]) for area_key in value.keys() if area_key != 'names']
        print(key, counts)
        if np.any(np.array(counts)!=1):
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
    