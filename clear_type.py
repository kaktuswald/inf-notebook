import os
import numpy as np
import pickle

from data_collection import load_collections
from define import define
from resources import resources_dirname

area = define.details_areas['clear_type']

filepath = os.path.join(resources_dirname, 'clear_type.res')
if os.path.exists(filepath):
    with open(filepath, 'rb') as f:
        table = pickle.load(f)
else:
    table = {}

def get_clear_type(image_details):
    np_value = np.array(image_details.crop(area)).flatten()

    uniques, counts = np.unique(np_value, return_counts=True)
    mode = uniques[np.argmax(counts)]

    if not mode in table.keys():
        return None

    return table[mode]

def larning(targets):
    global table

    table = {}
    for key, target in targets.items():
        value = target['value']
        np_value = target['np']

        uniques, counts = np.unique(np_value, return_counts=True)
        mode = uniques[np.argmax(counts)]

        if mode in table.keys() and table[mode] != value:
            print(mode, table[mode], value)
            print("NG")
            return
        else:
            table[mode] = value

    values = [*table.values()]
    uniques, counts = np.unique(np.array(values), return_counts=True)
    multicount_values = [value for value in np.where(counts>=2,uniques,None) if value is not None]
    if len(multicount_values) != 1 or multicount_values[0] != 'F-COMBO':
        print(multicount_values)
        print('NG')
        return
    
    for key, value in table.items():
        print(key, value)
    
    with open(filepath, 'wb') as f:
        pickle.dump(table, f)

def larning_clear_type():
    collections = load_collections()

    targets = {}
    for collection in collections:
        label = collection.label
        if collection.details is not None:
            image = collection.details

            if label['details']['clear_type'] != '':
                targets[collection.key] = {
                    'value': label['details']['clear_type'],
                    'np': np.array(image.crop(area)).flatten()
                }

    larning(targets)

if __name__ == '__main__':
    larning_clear_type()
