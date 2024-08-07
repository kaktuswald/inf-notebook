import numpy as np
from os.path import join
import json

from raw_image import raws_basepath

learningbase_direpath = 'learning'
mask_images_dirpath = join(learningbase_direpath, 'mask_images')

label_basics_filepath = join(raws_basepath, 'label.json')
label_collections_filepath = join(raws_basepath, 'label.json')

class RawLabel:
    labels = {}

    def __init__(self):
        self.load()

    def load(self):
        try:
            with open(label_basics_filepath) as f:
                self.labels = json.load(f)
        except Exception:
            self.labels = {}

    def save(self):
        with open(label_basics_filepath, 'w') as f:
            json.dump(self.labels, f, indent=2)

    def get(self, filename):
        if filename in self.labels:
            return self.labels[filename]
        
        return None
    
    def all(self):
        return self.labels.keys()

    def remove(self, filename):
        if filename in self.labels:
            del self.labels[filename]

    def update(self, filename, values):
        self.labels[filename] = values

def learning(targets, report):
    if len(targets) == 0:
        report.append_log('count: 0')
        return None

    patterns = []
    listeds = []
    for filename, np_value in targets.items():
        listed = np_value.tolist()
        if not listed in listeds:
            patterns.append(np_value)
            listeds.append(listed)
            report.saveimage_value(np_value, f'pattern{len(patterns):02}-{filename}')
    
    report.append_log(f'pattern count: {len(patterns)}')

    result = np.copy(patterns[0])
    for target in patterns[1:]:
        result = np.where(result|result==target, result, 0)

    if np.sum(result) == 0:
        report.append_log('Result equal 0')
        return None

    return result

def learning_multivalue(targets, report, maskvalue):
    if len(targets) == 0:
        report.append_log('count: 0')
        return None

    table = {}
    for value in targets.keys():
        keys = []
        for key, np_value in targets[value].items():
            bins = np.where(np_value.flatten()==maskvalue, 1, 0)
            hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
            tablekey = ''.join([format(v, '0x') for v in hexs])

            if not tablekey in table.keys():
                table[tablekey] = value
                keys.append(tablekey)
                report.append_log(f'{value}: {tablekey}')
                report.saveimage_value(np_value, f'{value}-pattern{len(keys):02}-{tablekey}-{key}.png')
    
    report.append_log(f'Key count: {len(table)}')

    if len(table) == 0:
        return None

    return table

