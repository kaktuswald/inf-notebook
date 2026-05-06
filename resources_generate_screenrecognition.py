import numpy as np
from random import shuffle
from os import mkdir
from os.path import join,exists
from json import load
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

from PIL import Image

from define import Playsides,define
from resources_generate import Report,load_raws,save_resource_serialized,registries_dirname
from resources_learning import learning

recognition_define_filename = 'define_recognition_screen.json'
recognition_define_filepath = join(registries_dirname, recognition_define_filename)

resource_filename = f'screenrecognition{define.screenrecognition_version}.res'

def load_define() -> dict:
    try:
        with open(recognition_define_filepath) as f:
            loaded = load(f)
    except Exception:
        print(f'{recognition_define_filepath}を読み込めませんでした。')
        return None
    
    ret = {
        'get_screen': {
            screenname: {
                'left': loaded['get_screen'][screenname]['left'],
                'top': loaded['get_screen'][screenname]['top'],
                'width': loaded['get_screen'][screenname]['width'],
                'height': loaded['get_screen'][screenname]['height'],
            } for screenname in loaded['get_screen'].keys()
        },
        'result': {
            'is_savable': {
                'patternarea': tuple(slice(ax[0], ax[1]) for ax in loaded['result']['is_savable']['patternarea']),
                'keyslice': tuple(slice(sl[0], sl[1], sl[2]) for sl in loaded['result']['is_savable']['keyslice']),
                'checkareas': {
                    key: tuple(
                        tuple(slice(sl[0], sl[1], sl[2]) for sl in ax)
                    ) for key, ax in loaded['result']['is_savable']['checkareas'].items()
                },
            },
            'has_loveletter': (
                slice(loaded['result']['has_loveletter'][0][0], loaded['result']['has_loveletter'][0][1]),
                slice(loaded['result']['has_loveletter'][1][0], loaded['result']['has_loveletter'][1][1]),
                loaded['result']['has_loveletter'][2],
            ),
            'playside': {
                playside: (
                    slice(loaded['result']['playside'][playside][0][0], loaded['result']['playside'][playside][0][1]),
                    slice(loaded['result']['playside'][playside][1][0], loaded['result']['playside'][playside][1][1]),
                    loaded['result']['playside'][playside][2],
                ) for playside in loaded['result']['playside'].keys()
            },
            'is_dead': {
                playside: (
                    slice(loaded['result']['is_dead'][playside][0][0], loaded['result']['is_dead'][playside][0][1]),
                    slice(loaded['result']['is_dead'][playside][1][0], loaded['result']['is_dead'][playside][1][1]),
                    loaded['result']['is_dead'][playside][2],
                ) for playside in loaded['result']['is_dead'].keys()
            },
        },
    }

    return ret

def generate_get_screen(raws):
    report_get_screen = Report('get_screen')
    
    reversed_areas = {}
    for k, v in recognition_define['get_screen'].items():
        left = v['left']
        bottom = define.height - v['top']
        right = left + v['width']
        top = bottom - v['height']
        reversed_areas[k] = (slice(top, bottom), slice(left, right))

    table = {}
    for filename, raw in raws.items():
        if not 'screenname' in raw.label.keys():
            continue

        screen = raw.label['screenname']
        if not screen in recognition_define['get_screen'].keys():
            continue
        
        if screen in table.keys():
            continue

        np_value_reverse = raw.np_value[::-1, :, ::-1]
        key_value = np_value_reverse[reversed_areas[screen]]
        key = np.sum(key_value)

        table[screen] = key
        report_get_screen.saveimage_value(key_value, f'{screen}-{filename}')
        report_get_screen.append_log(f'({filename}){screen}: {key}')
        
        if len(table) == len(recognition_define['get_screen']):
            break
        
    for filename, raw in raws.items():
        if not 'screenname' in raw.label.keys():
            continue

        screen = raw.label['screenname']
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
            report_get_screen.error(f'Failure {filename} {screen}: {values}')
            continue

        if len(results) >= 2:
            report_get_screen.error(f'Duplicate {filename} {screen}: {values}')
            continue

        if results[0] != screen:
            report_get_screen.error(f'Mismatch {filename} {screen}: {values}')
            continue
        
        report_get_screen.through()

    report_get_screen.report()

    if not report_get_screen.count_error:
        report.through()
    else:
        report.error('error get_screen')
    
    return {
        key: {
            'area': recognition_define['get_screen'][key],
            'value': table[key],
        } for key in table.keys()
    }

def generate_is_savable(raws):
    report_is_savable = Report('is_savable')

    append_dirpath = join(report_is_savable.report_dirpath, 'trimmed')
    if not exists(append_dirpath):
        mkdir(append_dirpath)

    patternarea = recognition_define['result']['is_savable']['patternarea']
    keyslice: tuple[slice] = recognition_define['result']['is_savable']['keyslice']
    checkareas = recognition_define['result']['is_savable']['checkareas']

    targets1 = {}
    for filename, raw in raws.items():
        if not 'screenname' in raw.label.keys() or raw.label['screenname'] != 'result':
            continue
        if not 'is_savable' in raw.label.keys() or not raw.label['is_savable']:
            continue

        trimmed = raw.np_value[patternarea]
        decoded = trimmed.tobytes()
        if not decoded in targets1.keys():
            targets1[decoded] = {}
        targets1[decoded][filename] = raw
    
    report_is_savable.append_log(f'count patterns: {len(targets1)}')

    ylist = [*range(patternarea[0].start, patternarea[0].stop-(keyslice[0].stop-keyslice[0].start-1))]
    xlist = [*range(patternarea[1].start, patternarea[1].stop-(keyslice[1].stop-keyslice[1].start-1))]
    randoms = [
        (
            slice(y+keyslice[0].start, y+keyslice[0].stop, keyslice[0].step),
            slice(x+keyslice[1].start, x+keyslice[1].stop, keyslice[1].step),
        ) for y in ylist for x in xlist
    ]

    shuffle(randoms)
    trycount = 0
    for candidate in randoms[:1000]:
        trycount += 1
        targets2 = {}
        for target in targets1.values():
            pixel = [*target.values()][0].np_value[candidate]
            key = ''.join([format(v, '02x') for v in pixel.flatten()])
            targets2[key] = target
        if len(targets1) == len(set(targets2.keys())):
            break
    
    report_is_savable.append_log(f'key search try count: {trycount}')

    if len(targets1) == len(set(targets2.keys())):
        keyposition = candidate

        sorted_keys = sorted([*targets2.keys()])
        for background_key in sorted_keys:
            report_is_savable.append_log(f'"{background_key}" {len(targets2[background_key])}({[*targets2[background_key].keys()][0]})')
        
        checktable = {}
        for background_key, targets in targets2.items():
            checktable[background_key] = {}
            filename, raw = [*targets.items()][0]

            image = Image.fromarray(raw.np_value[patternarea])
            image.save(join(append_dirpath, filename))

            for area_key, area in checkareas.items():
                value = raw.np_value[area]
                checktable[background_key][area_key] = value

            for filename, raw in targets.items():
                for area_key, area in checkareas.items():
                    value = raw.np_value[area]
                    if np.array_equal(value, checktable[background_key][area_key]):
                        report_is_savable.through()
                    else:
                        report_is_savable.error(f'Mismatch {background_key} {area_key} {filename}')
    else:
        report_is_savable.error('no valid position was found for the key.')

    report_is_savable.report()

    if not report_is_savable.count_error:
        report.through()
    else:
        report.error('error is_savable')
    
    if not report_is_savable.count_error:
        return {
            'keyposition': keyposition,
            'checkareas': checkareas,
            'checktable': checktable,
        }
    else:
        return None

def learning_has_loveletter(raws):
    report_has_loveletter = Report('has_loveletter')

    trimarea = recognition_define['result']['has_loveletter']

    learning_targets = {}
    evaluate_targets = {}
    for filename, raw in raws.items():
        if not 'screenname' in raw.label.keys() or raw.label['screenname'] != 'result':
            continue
        if not 'has_loveletter' in raw.label.keys():
            continue

        if raw.label['has_loveletter']:
            trimmed = raw.np_value[trimarea]
            learning_targets[filename] = trimmed
        evaluate_targets[filename] = raw
    
    report_has_loveletter.append_log(f'source count: {len(learning_targets)}')

    result = learning(learning_targets, report_has_loveletter)
    if result is None:
        report_has_loveletter.report()
        return

    for filename, raw in evaluate_targets.items():
        has_loveletter = raw.label['has_loveletter']
        trimmed = raw.np_value[trimarea]
        recoged = np.all((result==0)|(trimmed==result))
        if (recoged and has_loveletter) or (not recoged and not has_loveletter):
            report_has_loveletter.through()
        else:
            report_has_loveletter.saveimage_errorvalue(trimmed, filename)
            report_has_loveletter.error(f'Mismatch {has_loveletter} {filename}')

    report_has_loveletter.report()

    if not report_has_loveletter.count_error:
        report.through()
    else:
        report.error('error has_loveletter')
    
    return {
        'trimarea': trimarea,
        'value': result,
    }

def learning_playside(raws):
    report_playside = Report('playside')

    trimareas = recognition_define['result']['playside']

    learning_targets = {}
    evaluate_targets = {}
    for filename, raw in raws.items():
        if not 'screenname' in raw.label.keys() or raw.label['screenname'] != 'result':
            continue
        if not 'is_savable' in raw.label.keys() or raw.label['is_savable']:
            continue
        if not 'playside' in raw.label.keys() or not raw.label['playside'] in Playsides.values:
            continue

        playside = raw.label['playside']
        trimmed = raw.np_value[trimareas[playside]]
        learning_targets[filename] = trimmed

        evaluate_targets[filename] = raw
    
    report_playside.append_log(f'source count: {len(learning_targets)}')

    result = learning(learning_targets, report_playside)
    if result is None:
        report_playside.report()
        return

    for filename, raw in evaluate_targets.items():
        recoged = None
        for key, area in trimareas.items():
            if np.all((result==0)|(raw.np_value[area]==result)):
                recoged = key
        playside = raw.label['playside']
        if recoged == playside:
            report_playside.through()
        else:
            report_playside.saveimage_errorvalue(trimmed, filename)
            report_playside.error(f'Mismatch {recoged} {filename}')

    report_playside.report()

    if not report_playside.count_error:
        report.through()
    else:
        report.error('error playside')
    
    return {
        'trimareas': {
            playside: trimarea for playside, trimarea in trimareas.items()
        },
        'value': result,
    }

def learning_is_dead(raws):
    report_is_dead = Report('is_dead')

    trimareas = recognition_define['result']['is_dead']

    learning_targets = {}
    evaluate_targets = {}
    for filename, raw in raws.items():
        if not 'screenname' in raw.label.keys() or raw.label['screenname'] != 'result':
            continue
        if not 'is_dead' in raw.label.keys():
            continue
        if not 'playside' in raw.label.keys() or not raw.label['playside'] in Playsides.values:
            continue

        if raw.label['is_dead']:
            playside = raw.label['playside']
            trimmed = raw.np_value[trimareas[playside]]
            learning_targets[filename] = trimmed
        evaluate_targets[filename] = raw
    
    report_is_dead.append_log(f'source count: {len(learning_targets)}')

    result = learning(learning_targets, report_is_dead)
    if result is None:
        report_is_dead.report()
        return

    for filename, raw in evaluate_targets.items():
        is_dead = raw.label['is_dead']
        playside = raw.label['playside']
        trimmed = raw.np_value[trimareas[playside]]
        recoged = np.all((result==0)|(trimmed==result))
        if (recoged and is_dead) or (not recoged and not is_dead):
            report_is_dead.through()
        else:
            report_is_dead.saveimage_errorvalue(trimmed, filename)
            report_is_dead.error(f'Mismatch {is_dead} {filename}')

    report_is_dead.report()

    if not report_is_dead.count_error:
        report.through()
    else:
        report.error('error is_dead')
    
    return {
        'trimareas': {
            playside: trimarea for playside, trimarea in trimareas.items()
        },
        'value': result,
    }

if __name__ == '__main__':
    recognition_define = load_define()
    if recognition_define is None:
        exit()

    raws = load_raws()

    report = Report('screenrecognition')

    result = {
        'get_screen': generate_get_screen(raws),
        'result': {
            'is_savable': generate_is_savable(raws),
            'has_loveletter': learning_has_loveletter(raws),
            'playside': learning_playside(raws),
            'is_dead': learning_is_dead(raws),
        },
    }
    
    save_resource_serialized(resource_filename, result, True)

    report.report()
