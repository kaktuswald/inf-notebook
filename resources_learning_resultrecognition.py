import json
from sys import exit
from os.path import join,isfile
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

from PIL import Image
import numpy as np
import json5

from define import define
from data_collection import (
    label_resultjudges_filepath,
    label_resulttimings_filepath,
    label_resultcombobreak_filepath,
    images_resultjudges_basepath,
    images_resulttimings_basepath,
    images_resultcombobreak_basepath,
)
from resources_generate import Report,save_resource_serialized,registries_dirname

recognition_define_filename = 'define_recognition_result.json5'

label_filepaths = {
    'judges': label_resultjudges_filepath,
    'timings': label_resulttimings_filepath,
    'combobreak': label_resultcombobreak_filepath,
}

images_basepaths = {
    'judges': images_resultjudges_basepath,
    'timings': images_resulttimings_basepath,
    'combobreak': images_resultcombobreak_basepath,
}

recognition_define_filepath = join(registries_dirname, recognition_define_filename)

class ImageValues():
    def __init__(self, np_value, label):
        self.np_value = np_value
        self.label = label

def load_images(images_basepath: str, labels:dict) -> dict:
    keys = [key for key in labels.keys()]

    imagevaleus = {}
    for filename in keys:
        if 'ignore' in labels[filename].keys() and labels[filename]['ignore']:
            continue

        filepath = join(images_basepath, filename)
        if not isfile(filepath):
            continue

        np_value = np.array(Image.open(filepath), dtype=np.uint8)
        imagevaleus[filename] = ImageValues(np_value, labels[filename])
    
    return imagevaleus

def load_define(define_filepath: str) -> dict:
    try:
        with open(define_filepath) as f:
            ret = json5.load(f)
    except Exception:
        report.error(f'load failed {define_filepath}')
        return None

    return ret

def learning_number(name: str, define: dict, targets: list):
    report_number = Report(name)

    digittrim = (
        slice(define['digittrim'][0][0], define['digittrim'][0][1], define['digittrim'][0][2]),
        slice(define['digittrim'][1][0], define['digittrim'][1][1], define['digittrim'][1][2]),
    )

    table = {}
    targetkeys = {}
    for key, target in targets.items():
        trimmed = target[0]
        value = int(target[1])

        leastvalue = value % 10
        splitted = np.hsplit(trimmed, define['digitcount'])
        trimmed_once = splitted[-1][digittrim]
        bins = np.where(trimmed_once==define['maskvalue'], 1, 0)
        packed = np.packbits(bins)
        tablekey = packed.tobytes().hex()
        if not tablekey in table or not leastvalue in table.values():
            table[tablekey] = leastvalue
            targetkeys[leastvalue] = key
    
    for value in range(10):
        keys = [k for k, v in table.items() if v == value]
        if not len(keys):
            report_number.append_log(f'Not found key {value}')
        else:
            report_number.append_log(f'{value}: {keys} ({targetkeys[value]})')

    for key, target in targets.items():
        trimmed = target[0]
        value = int(target[1])

        result = 0
        for dig in range(define['digitcount']):
            splitted = np.hsplit(trimmed, define['digitcount'])
            trimmed_once = splitted[-(dig+1)][digittrim]
            bins = np.where(trimmed_once==define['maskvalue'], 1, 0)
            packed = np.packbits(bins)
            tablekey = packed.tobytes().hex()
            if not tablekey in table.keys():
                break
            result += 10 ** dig * table[tablekey]
        
        if value == result:
            report_number.through()
        else:
            report_number.saveimage_errorvalue(trimmed, f'{key}.png')
            report_number.error(f'Mismatch value {result} {value} {key}')
    
    report_number.report()
    
    if not report_number.count_error:
        report.through()
    else:
        report.error('Error number')

    return {
        'digittrim': digittrim,
        'table': table
    }

if __name__ == '__main__':
    report = Report('resultrecognition')

    recognitiondefine = load_define(recognition_define_filepath)
    if recognitiondefine is None:
        report.error('not exist define file')
        report.report()
        exit()

    resource = {}

    for key in ['judges', 'timings', 'combobreak']:
        try:
            with open(label_filepaths[key]) as f:
                labels = json.load(f)
        except Exception:
            report.error(f'loading error {label_filepaths[key]}')
            continue

        imagevalues = load_images(images_basepaths[key], labels)

        if key in ['judges', 'timings']:
            trims = {}
            for valuekey, trim in recognitiondefine[key]['trims'].items():
                trims[valuekey] = (slice(trim[0][0], trim[0][1]), slice(trim[1][0], trim[1][1]), slice(trim[2]))
            
            targets = {}
            for labelkey, imagevalue in imagevalues.items():
                for valuekey, value in imagevalue.label.items():
                    if value != '':
                        trimmed = imagevalue.np_value[trims[valuekey]]
                        targets[f'{labelkey}_{valuekey}_{value}'] = (trimmed, value,)

            learningresult = learning_number(
                f'resultrecognition_{key}',
                recognitiondefine[key],
                targets,
            )

            resource[key] = {
                'trims': trims,
                'digitcount': recognitiondefine[key]['digitcount'],
                'digittrim': learningresult['digittrim'],
                'maskvalue': recognitiondefine[key]['maskvalue'],
                'table': learningresult['table'],
            }
        
        if key == 'combobreak':
            trim = (
                slice(
                    recognitiondefine[key]['trim'][0][0],
                    recognitiondefine[key]['trim'][0][1],
                ),
                slice(
                    recognitiondefine[key]['trim'][1][0],
                    recognitiondefine[key]['trim'][1][1],
                ),
                slice(recognitiondefine[key]['trim'][2]),
            )
            
            targets = {}
            for labelkey, imagevalue in imagevalues.items():
                value = imagevalue.label['combobreak']

                if value != '':
                    trimmed = imagevalue.np_value[trim]
                    targets[f'{labelkey}_{value}'] = (trimmed, value,)

            learningresult = learning_number(
                f'resultrecognition_{key}',
                recognitiondefine[key],
                targets,
            )

            resource[key] = {
                'trim': trim,
                'digitcount': recognitiondefine[key]['digitcount'],
                'digittrim': learningresult['digittrim'],
                'maskvalue': recognitiondefine[key]['maskvalue'],
                'table': learningresult['table'],
            }

    filename = f'resultrecognition{define.resultrecognition_version}.res'
    save_resource_serialized(filename, resource, True)
    
    report.report()
