import numpy as np
from sys import argv
from random import shuffle
from os import mkdir
from os.path import join,exists
from PIL import Image

from define import define
from resources_generate import Report,load_raws,save_resource_serialized

error_file_output_count = 3

resourcenames = {
    'get_screen': 'get_screen.res',
    'is_savable': 'is_savable.res',
}

def generate_get_screen(raws):
    resourcename = resourcenames['get_screen']

    report = Report(resourcename)
    
    reversed_areas = {}
    for k, v in define.screens.items():
        left = v['left']
        bottom = define.height - v['top']
        right = left + v['width']
        top = bottom - v['height']
        reversed_areas[k] = (slice(top, bottom), slice(left, right))

    table = {}
    for filename, raw in raws.items():
        if not 'screen' in raw.label.keys():
            continue

        screen = raw.label['screen']
        if not screen in define.screens.keys():
            continue
        
        if screen in table.keys():
            continue

        np_value_reverse = raw.np_value[::-1, :, ::-1]
        key_value = np_value_reverse[reversed_areas[screen]]
        key = np.sum(key_value)

        table[screen] = key
        report.saveimage_value(key_value, f'{screen}-{filename}')
        report.append_log(f'({filename}){screen}: {key}')
        
        if len(table) == len(define.screens):
            break
        
    for filename, raw in raws.items():
        if not 'screen' in raw.label.keys():
            continue

        screen = raw.label['screen']
        if not screen in table.keys():
            continue

        np_value_reverse = raw.np_value[::-1, :, ::-1]

        results = []
        values = []
        for k, v in table.items():
            value = np.sum(np_value_reverse[reversed_areas[k]])
            if v == value:
                results.append(k)
            values.append((k, value))

        if len(results) == 0:
            report.error(f'Failure {filename} {screen}: {values}')
            continue

        if len(results) >= 2:
            report.error(f'Duplicate {filename} {screen}: {values}')
            continue

        if results[0] != screen:
            report.error(f'Mismatch {filename} {screen}: {values}')
            continue
        
        report.through()

    save_resource_serialized(resourcename, table)

    report.report()

def generate_is_savable(raws):
    resourcename = resourcenames['is_savable']

    report = Report(resourcename)

    append_dirpath = join(report.report_dirpath, 'trimmed')
    if not exists(append_dirpath):
        mkdir(append_dirpath)

    patternarea = (slice(60, 690), slice(810, 1110))

    targets1 = {}
    for filename, raw in raws.items():
        if not 'screen' in raw.label.keys() or raw.label['screen'] != 'result':
            continue
        if not 'is_savable' in raw.label.keys() or not raw.label['is_savable']:
            continue

        trimmed = raw.np_value[patternarea]
        decoded = trimmed.tobytes()
        if not decoded in targets1.keys():
            targets1[decoded] = {}
        targets1[decoded][filename] = raw
    
    report.append_log(f'count patterns: {len(targets1)}')

    ylist = [*range(patternarea[0].start, patternarea[0].stop)]
    xlist = [*range(patternarea[1].start, patternarea[1].stop)]
    randoms = [(y, x) for y in ylist for x in xlist]
    shuffle(randoms)
    trycount = 0
    for background_key_position in randoms:
        trycount += 1
        targets2 = {}
        for target in targets1.values():
            pixel = [*target.values()][0].np_value[background_key_position]
            key = ''.join([format(v, '02x') for v in pixel])
            targets2[key] = target
        if len(targets1) == len(set(targets2.keys())):
            break

    report.append_log(f'key search try count: {trycount}')

    sorted_keys = sorted([*targets2.keys()])
    for background_key in sorted_keys:
        report.append_log(f'"{background_key}" {len(targets2[background_key])}({[*targets2[background_key].keys()][0]})')
    
    table = {'keyposition': background_key_position, 'areas': {}}
    for background_key, targets in targets2.items():
        table['areas'][background_key] = {}
        filename, raw = [*targets.items()][0]

        image = Image.fromarray(raw.np_value[patternarea])
        image.save(join(append_dirpath, filename))

        for area_key, area in define.result_check.items():
            value = raw.np_value[area]
            table['areas'][background_key][area_key] = value
            report.saveimage_value(value, f'{background_key}-{area_key}-{filename}')

        for filename, raw in targets.items():
            for area_key, area in define.result_check.items():
                value = raw.np_value[area]
                if np.array_equal(value, table['areas'][background_key][area_key]):
                    report.through()
                else:
                    report.saveimage_errorvalue(value, filename)
                    report.error(f'Mismatch {background_key} {area_key} {filename}')

    save_resource_serialized(resourcename, table)

    report.report()

if __name__ == '__main__':
    if len(argv) == 1:
        print('please argment.')
        exit()

    raws = load_raws()

    if '-all' in argv or '-get_screen' in argv:
        generate_get_screen(raws)

    if '-all' in argv or '-is_savable' in argv:
        generate_is_savable(raws)
    