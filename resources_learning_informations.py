from PIL import Image
import json
from sys import exit
from os import mkdir
from os.path import join,isfile,exists
import numpy as np

from define import define
import data_collection as dc
from resources import load_resource_serialized
from resources_generate import Report,save_resource_serialized,registries_dirname,report_dirname
from resources_learning import learning_multivalue

recognition_define_filename = 'define_recognition_informations.json'

report_organize_filename = 'organize.txt'
report_missing_musics_filename = 'musics_missing_in_arcade.txt'

recognition_define_filepath = join(registries_dirname, recognition_define_filename)

report_basedir_musicrecog = join(report_dirname, 'musicrecog')

class Informations():
    def __init__(self, np_value, label):
        self.np_value = np_value
        self.label = label

def load_informations(labels):
    def is_using(key):
        if not 'informations' in labels[key].keys() or labels[key]['informations'] is None:
            return False
        if not 'ignore' in labels[key]['informations']:
            return True
        
        return not labels[key]['informations']['ignore']
    
    keys = [key for key in labels.keys() if is_using(key)]

    informations = {}
    for key in keys:
        filename = f'{key}.png'
        filepath = join(dc.informations_basepath, filename)
        if not isfile(filepath):
            continue

        image = Image.open(filepath)
        if image.height == define.informations_trimsize[1]:
            np_value = np.array(image, dtype=np.uint8)
        else:
            np_value = np.zeros((define.informations_trimsize[1], define.informations_trimsize[0], 3), dtype=np.uint8)
            np_value[define.informations_trimsize[1] - image.height:, :, :] = np.array(image)
        informations[key] = Informations(np_value, labels[key]['informations'])
    
    return informations

def load_define():
    try:
        with open(recognition_define_filepath) as f:
            ret = json.load(f)
    except Exception:
        print(f"{recognition_define_filepath}を読み込めませんでした。")
        return None
    
    ret['play_mode']['trim'] = (
        slice(ret['play_mode']['trim'][0][0], ret['play_mode']['trim'][0][1]),
        slice(ret['play_mode']['trim'][1][0], ret['play_mode']['trim'][1][1]),
        ret['play_mode']['trim'][2]
    )

    ret['difficulty']['trim'] = (
        slice(ret['difficulty']['trim'][0][0], ret['difficulty']['trim'][0][1]),
        slice(ret['difficulty']['trim'][1][0], ret['difficulty']['trim'][1][1])
    )
    ret['difficulty']['trimlevel'] = (
        slice(ret['difficulty']['trimlevel'][0][0], ret['difficulty']['trimlevel'][0][1]),
        slice(ret['difficulty']['trimlevel'][1][0], ret['difficulty']['trimlevel'][1][1])
    )

    ret['notes']['trim'] = (
        slice(ret['notes']['trim'][0][0], ret['notes']['trim'][0][1]),
        slice(ret['notes']['trim'][1][0], ret['notes']['trim'][1][1]),
        ret['notes']['trim'][2]
    )
    ret['notes']['trimnumber'] = (
        slice(ret['notes']['trimnumber'][0][0], ret['notes']['trimnumber'][0][1]),
        slice(ret['notes']['trimnumber'][1][0], ret['notes']['trimnumber'][1][1])
    )

    ret['playspeed']['trim'] = (
        slice(ret['playspeed']['trim'][0][0], ret['playspeed']['trim'][0][1]),
        slice(ret['playspeed']['trim'][1][0], ret['playspeed']['trim'][1][1]),
        ret['playspeed']['trim'][2]
    )

    ret['music']['trim'] = (
        slice(ret['music']['trim'][0][0], ret['music']['trim'][0][1]),
        slice(ret['music']['trim'][1][0], ret['music']['trim'][1][1])
    )

    return ret

def filter(targets, report, define):
    result = []
    grays = {}
    blues = {}
    reds = {}

    width = define['trim'][1].stop - define['trim'][1].start

    blue_lower = np.array([np.tile([[v2[0] for v2 in v1]], (width, 1)) for v1 in define['blue_thresholds']], dtype=np.uint8)
    blue_upper = np.array([np.tile([[v2[1] for v2 in v1]], (width, 1)) for v1 in define['blue_thresholds']], dtype=np.uint8)
    red_lower = np.array([np.tile([[v2[0] for v2 in v1]], (width, 1)) for v1 in define['red_thresholds']], dtype=np.uint8)
    red_upper = np.array([np.tile([[v2[1] for v2 in v1]], (width, 1)) for v1 in define['red_thresholds']], dtype=np.uint8)
    gray_lower = np.array([np.tile(v[0], (width, 3)) for v in define['gray_thresholds']], dtype=np.uint8)
    gray_upper = np.array([np.tile(v[1], (width, 3)) for v in define['gray_thresholds']], dtype=np.uint8)

    for music, values in targets.items():
        result.append(f'{music}: {len(values)}')
        for key, value in values.items():
            filtereds = []
            for i in range(value.shape[2]):
                filtereds.append(np.where((blue_lower[:,:,i]<=value[:,:,i])&(value[:,:,i]<=blue_upper[:,:,i]), value[:,:,i], 0))
            blue = np.where((filtereds[0]!=0)&(filtereds[1]!=0)&(filtereds[2]!=0), filtereds[2], 0)

            filtereds = []
            for i in range(value.shape[2]):
                filtereds.append(np.where((red_lower[:,:,i]<=value[:,:,i])&(value[:,:,i]<=red_upper[:,:,i]), value[:,:,i], 0))
            red = np.where((filtereds[0]!=0)&(filtereds[1]!=0)&(filtereds[2]!=0), filtereds[0], 0)

            filtereds = []
            for i in range(value.shape[2]):
                filtereds.append(np.where((gray_lower[:,:,i]<=value[:,:,i])&(value[:,:,i]<=gray_upper[:,:,i]), value[:,:,i], 0))
            gray = np.where((filtereds[0]==filtereds[1])&(filtereds[0]==filtereds[2]), filtereds[0], 0)

            blue_count = np.count_nonzero(blue)
            red_count = np.count_nonzero(red)
            gray_count = np.count_nonzero(gray)
            result.append(f'{key} blue: {blue_count} red: {red_count}, gray: {gray_count}')

            max_count = max(blue_count, red_count, gray_count)
            if max_count == blue_count:
                if not music in blues.keys():
                    blues[music] = {}
                blues[music][key] = blue
            if max_count == red_count:
                if not music in reds.keys():
                    reds[music] = {}
                reds[music][key] = red
            if max_count == gray_count:
                if not music in grays.keys():
                    grays[music] = {}
                grays[music][key] = gray
    
    report.append_log(f'Gray filter music count: {len(grays)}')
    report.append_log(f'Blue filter music count: {len(blues)}')
    report.append_log(f'Red filter music count: {len(reds)}')

    result_report_filepath = join(report_basedir_musicrecog, 'filtertype.txt')
    with open(result_report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(result))
    
    factors = {
        'blue': {
            'lower': blue_lower,
            'upper': blue_upper,
        },
        'red': {
            'lower': red_lower,
            'upper': red_upper,
        },
        'gray': {
            'lower': gray_lower,
            'upper': gray_upper,
        }
    }

    return grays, blues, reds, factors

def generate_mask(targets, report, name):
    report.append_log(f'Generate mask {name}')

    mask = np.full(musicshape, 1)
    mask_report = {}
    for music, values in targets.items():
        if not music in mask_report.keys():
            mask_report[music] = {}
        for key, current in values.items():
            stacked = np.stack([np.where(current!=target, 1, 0) for target in values.values()])
            result = np.any(stacked, axis=0)
            mask = np.where(result, 0, mask)
            mask_report[music][key] = np.stack(np.where(result)).T
    report.append_log(f'Mask pixel count: {np.count_nonzero(mask)}')
    
    output = []
    for music in sorted(mask_report.keys()):
        output.append(music)
        for key, value in mask_report[music].items():
            if len(value) > 0:
                output.append(f"{key}: ({len(value)}){' '.join([str(p) for p in value[:5]])}")

    masks_report_filepath = join(report_basedir_musicrecog, f'report_mask_{name}.txt')
    with open(masks_report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))

    report.saveimage_value(np.where(mask==0,False,True), f'mask_{name}.png')

    return mask

def filter_mask(targets, mask):
    mask_filtereds = {}
    for music, values in targets.items():
        mask_filtereds[music] = {}
        for key, value in values.items():
            mask_filtereds[music][key] = np.where(mask==1,value,0)
    return mask_filtereds

def learning_music(targets, report, name):
    map = {}

    inspect = {}
    musicnotuniques = {}
    for music, values in targets.items():
        for key, value in values.items():
            mapkeys = []
            for height in range(value.shape[0]):
                unique, counts = np.unique(value[height], return_counts=True)
                if len(unique) > 1:
                    index = -np.argmax(np.flip(counts[1:])) - 1
                    intensity = unique[index]
                    bins = np.where(value[height]==intensity, 1, 0)
                    hexs = bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
                    mapkeys.append(f"{height:02d}{''.join([format(v, '0x') for v in hexs])}")
                else:
                    mapkeys.append(f'{height:02d}')
            
            if len(mapkeys) == 0:
                report.error(f'Not created mapkey {name} {music}: {key}')
                continue

            maptarget = map
            for mapkey in mapkeys[:-1]:
                if not mapkey in maptarget:
                    maptarget[mapkey] = {}
                maptarget = maptarget[mapkey]
            maptarget[mapkeys[-1]] = music
            
            concatenatekey = '+'.join(mapkeys)

            if not concatenatekey in inspect.keys():
                inspect[concatenatekey] = {}
            inspect[concatenatekey][music] = {'key': key, 'value': value}

            if not music in musicnotuniques.keys():
                musicnotuniques[music] = {}
            musicnotuniques[music][concatenatekey] = {'key': key, 'value': value}

    report_inspect = []
    for tablekey, values in inspect.items():
        setted = set(values.keys())
        count = len(setted)
        report_inspect.append(f"{tablekey}:")
        for music, item in values.items():
            report_inspect.append(f"  {music}: {item['key']}")
        if count >= 2:
            report.error(f'duplicate key: {tablekey})')
            for k, v in values.items():
                report.error(f"{v['key']}: {k})")
            for music, item in values.items():
                report.saveimage_errorvalue(item['value'], f"_{item['key']}.png")

    inspectresult_report_filepath = join(report_basedir_musicrecog, f'inspect_{name}.txt')
    with open(inspectresult_report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(report_inspect))

    report_notuniques = []
    for music, values in musicnotuniques.items():
        setted = set(values.keys())
        count = len(setted)
        if count >= 2:
            report_notuniques.append(f'not unique: {music}({count})')
            for tablekey, item in values.items():
                report_notuniques.append(f"  {tablekey}: {item['key']}")
                report.saveimage_errorvalue(item['value'], f"_{item['key']}.png")

    notuniques_report_filepath = join(report_basedir_musicrecog, f'noteunique_{name}.txt')
    with open(notuniques_report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(report_notuniques))

    return map

def organize(informations):
    difficulties = {}
    for difficulty in define.value_list['difficulties']:
        difficulties[difficulty] = []
    levels = {}
    for level in define.value_list['levels']:
        levels[level] = []

    result = {}
    for key, information in informations.items():
        label = information.label

        if not 'difficulty' in label.keys() or label['difficulty'] != '':
            continue
        if not 'level' in label.keys() or label['level'] != '':
            continue
        if not 'music' in label.keys() or label['music'] != '':
            continue
        if not 'notes' in label.keys() or label['notes'] != '':
            continue

        difficulty = label['difficulty']
        level = label['level']
        music = label['music']
        notes = label['notes']

        if not music in result.keys():
            result[music] = {}
        
        result[music][difficulty] = [level, notes]

        if not music in difficulties[difficulty]:
            difficulties[difficulty].append(music)
        if not music in levels[level]:
            levels[level].append(music)
    
    output = []
    output.append(f'Music count: {len(result)}')
    for key, value in difficulties.items():
        output.append(f'{key}: {len(value)}')
    for key, value in levels.items():
        output.append(f'{key}: {len(value)}')
    for music, values in result.items():
        for difficulty, values in values.items():
            output.append(f'{music}: {difficulty} {values[0]} {values[1]}')

    if not exists(report_dirname):
        mkdir(report_dirname);
    
    report_filepath = join(report_dirname, report_organize_filename)
    with open(report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))

def outputtable(table):
    def recursive(sp, t, output):
        for key, value in t.items():
            if type(value) is dict:
                output.append(f"{' '*sp}{key}: {{")
                recursive(sp+2, value, output)
                output.append(f"{' '*sp}}}")
            else:
                output.append(f"{' '*sp}{key}: {value}")

    output = []
    recursive(0, table, output)

    report_filepath = join(report_dirname, 'table.txt')
    with open(report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))

def learning_playmode(informations):
    resourcename = 'playmode'

    report = Report(resourcename)

    learning_targets = {}
    evaluate_targets = {}
    for key, target in informations.items():
        if not 'play_mode' in target.label.keys() or target.label['play_mode'] == '':
            continue
        
        value = target.label['play_mode']
        trimmed = target.np_value[informations_define['play_mode']['trim']]
        if not value in learning_targets.keys():
            learning_targets[value] = {}
        learning_targets[value][key] = trimmed

        evaluate_targets[key] = target
    
    report.append_log(f'Source count: {len(learning_targets)}')

    table = learning_multivalue(learning_targets, report, informations_define['play_mode']['maskvalue'])
    if table is None:
        report.report()
        return

    for key, target in evaluate_targets.items():
        trimmed = target.np_value[informations_define['play_mode']['trim']].flatten()
        bins = np.where(trimmed==informations_define['play_mode']['maskvalue'], 1, 0)
        hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
        tablekey = ''.join([format(v, '0x') for v in hexs])

        result = None
        if tablekey in table.keys():
            result = table[tablekey]
        
        if result == target.label['play_mode']:
            report.through()
        else:
            report.saveimage_errorvalue(trimmed, f'{key}.png')
            report.error(f'Mismatch {result} {key}')

    report.report()

    return {
        'trim': informations_define['play_mode']['trim'],
        'maskvalue': informations_define['play_mode']['maskvalue'],
        'table': table
    }

def learning_difficulty(informations):
    resourcename = 'difficulty'

    report = Report(resourcename)

    evaluate_targets = {}
    table = {'difficulty': {}, 'level': {}}
    result = {}
    for key, target in informations.items():
        if not 'difficulty' in target.label.keys() or target.label['difficulty'] == '':
            continue
        if not 'level' in target.label.keys() or target.label['level'] == '':
            continue
        
        difficulty = target.label['difficulty']
        level = target.label['level']
        
        trimmed = target.np_value[informations_define['difficulty']['trim']].astype(np.uint32)
        converted = trimmed[:,:,0]*0x10000+trimmed[:,:,1]*0x100+trimmed[:,:,2]

        uniques, counts = np.unique(converted, return_counts=True)
        difficultykey = uniques[np.argmax(counts)]
        
        if not difficultykey in table['difficulty'].keys():
            table['difficulty'][difficultykey] = difficulty
            result[difficulty] = {'log': f'difficulty {difficulty}: {difficultykey}({key})', 'levels': {}}
        
        leveltrimmed = converted[informations_define['difficulty']['trimlevel']].flatten()
        bins = np.where(leveltrimmed==difficultykey, 1, 0)
        hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
        levelkey = ''.join([format(v, '0x') for v in hexs])

        if not difficulty in table['level'].keys():
            table['level'][difficulty] = {}
        if not levelkey in table['level'][difficulty].keys():
            table['level'][difficulty][levelkey] = level
            result[difficulty]['levels'][level] = f'level {difficulty} {level}: {levelkey}({key})'

        evaluate_targets[key] = target
    
    if len(table['difficulty']) != len(define.value_list['difficulties']):
        report.error(f'Duplicate difficulty key')
        for key, difficulty in table['difficulty'].items():
            report.error(f'{key}: {difficulty}')

    for difficulty in define.value_list['difficulties']:
        if difficulty in result.keys():
            report.append_log(result[difficulty]['log'])
            for level in define.value_list['levels']:
                if level in result[difficulty]['levels'].keys():
                    report.append_log(result[difficulty]['levels'][level])

    
    report.append_log(f'Source count: {len(evaluate_targets)}')

    for key, target in evaluate_targets.items():
        trimmed = target.np_value[informations_define['difficulty']['trim']].astype(np.uint32)
        converted = trimmed[:,:,0]*0x10000+trimmed[:,:,1]*0x100+trimmed[:,:,2]

        uniques, counts = np.unique(converted, return_counts=True)
        difficultykey = uniques[np.argmax(counts)]

        difficulty = None
        if difficultykey in table['difficulty'].keys():
            difficulty = table['difficulty'][difficultykey]

        if difficulty != target.label['difficulty']:
            report.saveimage_errorvalue(converted, f'{key}.png')
            report.error(f'Mismatch difficulty {difficulty} {key}')
            continue

        leveltrimmed = converted[informations_define['difficulty']['trimlevel']].flatten()
        bins = np.where(leveltrimmed==difficultykey, 1, 0)
        hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
        levelkey = ''.join([format(v, '0x') for v in hexs])

        level = None
        if levelkey in table['level'][difficulty].keys():
            level = table['level'][difficulty][levelkey]

        if level != target.label['level']:
            report.saveimage_errorvalue(trimmed, f'{key}.png')
            report.error(f"Mismatch level {difficulty} {level} {target.label['level']} {levelkey} {key}")
            continue

        report.through()

    report.report()

    return {
        'trim': informations_define['difficulty']['trim'],
        'trimlevel': informations_define['difficulty']['trimlevel'],
        'table': table
    }

def learning_notes(informations):
    resourcename = 'notes'

    report = Report(resourcename)

    evaluate_targets = {}
    table = {}
    result = {}
    for key, target in informations.items():
        if not 'notes' in target.label.keys() or target.label['notes'] == '':
            continue
        
        value = int(target.label['notes'])
        trimmed = target.np_value[informations_define['notes']['trim']]
        splited = np.hsplit(trimmed, informations_define['notes']['digit'])

        pos = informations_define['notes']['digit'] - 1
        while value != 0 and pos > 0:
            trimmed_once = splited[pos][informations_define['notes']['trimnumber']]
            bins = np.where(trimmed_once==informations_define['notes']['maskvalue'], 1, 0).flatten()
            hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
            tablekey = ''.join([format(v, '0x') for v in hexs])

            if not tablekey in table.keys():
                table[tablekey] = value % 10
                result[value % 10] = f'{value % 10}: {tablekey}'
                report.saveimage_value(trimmed_once, f'{value % 10}-{key}.png')

            value = value // 10
            pos -= 1

        evaluate_targets[key] = target
    
    report.append_log(f'key count: {len(table)}')
    for key in sorted(result.keys()):
        report.append_log(result[key])

    for key, target in evaluate_targets.items():
        trimmed = target.np_value[informations_define['notes']['trim']]
        splited = np.hsplit(trimmed, informations_define['notes']['digit'])

        value = 0
        pos = 3
        for pos in range(4):
            trimmed_once = splited[pos][informations_define['notes']['trimnumber']]
            bins = np.where(trimmed_once==informations_define['notes']['maskvalue'], 1, 0).flatten()
            hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
            tablekey = ''.join([format(v, '0x') for v in hexs])
            if tablekey in table.keys():
                value = value * 10 + table[tablekey]

        if value == int(target.label['notes']):
            report.through()
        else:
            report.saveimage_errorvalue(trimmed, f'{key}.png')
            report.error(f"Mismatch {value} {target.label['notes']} {key}")

    report.report()

    return {
        'trim': informations_define['notes']['trim'],
        'trimnumber': informations_define['notes']['trimnumber'],
        'maskvalue': informations_define['notes']['maskvalue'],
        'digit': informations_define['notes']['digit'],
        'table': table
    }

def learning_playspeed(informations):
    resourcename = 'playspeed'

    report = Report(resourcename)

    learning_targets = {}
    evaluate_targets = {}
    for key, target in informations.items():
        if not 'playspeed' in target.label.keys() or target.label['playspeed'] == '':
            continue
        
        value = target.label['playspeed']
        trimmed = target.np_value[informations_define['playspeed']['trim']]
        if not value in learning_targets.keys():
            learning_targets[value] = {}
        learning_targets[value][key] = trimmed

        evaluate_targets[key] = target
    
    report.append_log(f'Source count: {len(learning_targets)}')

    table = learning_multivalue(learning_targets, report, informations_define['playspeed']['maskvalue'])
    if table is None:
        report.report()
        return

    for key, target in evaluate_targets.items():
        trimmed = target.np_value[informations_define['playspeed']['trim']].flatten()
        bins = np.where(trimmed==informations_define['playspeed']['maskvalue'], 1, 0)
        hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
        tablekey = ''.join([format(v, '0x') for v in hexs])

        result = None
        if tablekey in table.keys():
            result = table[tablekey]
        
        if result == target.label['playspeed']:
            report.through()
        else:
            report.saveimage_errorvalue(trimmed, f'{key}.png')
            report.error(f'Mismatch {result} {key}')

    report.report()

    return {
        'trim': informations_define['playspeed']['trim'],
        'maskvalue': informations_define['playspeed']['maskvalue'],
        'table': table,
    }

def learning_musics(informations):
    resourcename = 'musicrecog'

    report = Report(resourcename)

    report.append_log(f'File count: {len(informations)}')

    targets = {}
    count = 0
    for key, target in informations.items():
        if not 'music' in target.label.keys() or target.label['music'] is None:
            continue

        if not target.label['music'] in targets.keys():
            targets[target.label['music']] = {}
        targets[target.label['music']][key] = target.np_value[informations_define['music']['trim']]
        count += 1
    
    report.append_log(f'Source count: {count}')
    report.append_log(f'Music count: {len(targets)}')

    for music in targets.keys():
        encoded = music.encode('UTF-8').hex()
        if len(encoded) > 240:
            report.error(f'Record file name too long: {music}')

    grays, blues, reds, factors = filter(
        targets,
        report,
        informations_define['music']
    )
    
    mask_gray = generate_mask(grays, report, 'gray')
    mask_blue = generate_mask(blues, report, 'blue')
    mask_red = generate_mask(reds, report, 'red')

    filtered_grays = filter_mask(grays, mask_gray)
    filtered_blues = filter_mask(blues, mask_blue)
    filtered_reds = filter_mask(reds, mask_red)

    table_gray = learning_music(filtered_grays, report, 'gray')
    table_blue = learning_music(filtered_blues, report, 'blue')
    table_red = learning_music(filtered_reds, report, 'red')

    musics = sorted([*targets.keys()])

    outputtable({'gray': table_gray, 'blue': table_blue, 'red': table_red})

    blue_lower = factors['blue']['lower']
    blue_upper = factors['blue']['upper']
    red_lower = factors['red']['lower']
    red_upper = factors['red']['upper']
    gray_lower = factors['gray']['lower']
    gray_upper = factors['gray']['upper']

    for key, target in informations.items():
        if not 'music' in target.label.keys() or target.label['music'] is None:
            continue
        music = target.label['music']

        trimmed = target.np_value[informations_define['music']['trim']]

        filtereds = []
        for i in range(trimmed.shape[2]):
            filtereds.append(np.where((blue_lower[:,:,i]<=trimmed[:,:,i])&(trimmed[:,:,i]<=blue_upper[:,:,i]), trimmed[:,:,i], 0))
        blue = np.where((filtereds[0]!=0)&(filtereds[1]!=0)&(filtereds[2]!=0), filtereds[2], 0)

        filtereds = []
        for i in range(trimmed.shape[2]):
            filtereds.append(np.where((red_lower[:,:,i]<=trimmed[:,:,i])&(trimmed[:,:,i]<=red_upper[:,:,i]), trimmed[:,:,i], 0))
        red = np.where((filtereds[0]!=0)&(filtereds[1]!=0)&(filtereds[2]!=0), filtereds[0], 0)

        filtereds = []
        for i in range(trimmed.shape[2]):
            filtereds.append(np.where((gray_lower[:,:,i]<=trimmed[:,:,i])&(trimmed[:,:,i]<=gray_upper[:,:,i]), trimmed[:,:,i], 0))
        gray = np.where((filtereds[0]==filtereds[1])&(filtereds[0]==filtereds[2]), filtereds[0], 0)

        gray_count = np.count_nonzero(gray)
        blue_count = np.count_nonzero(blue)
        red_count = np.count_nonzero(red)
        max_count = max(gray_count, blue_count, red_count)
        if max_count == gray_count:
            masked = np.where(mask_gray==1,gray,0)
            tabletarget = table_gray
        if max_count == blue_count:
            masked = np.where(mask_blue==1,blue,0)
            tabletarget = table_blue
        if max_count == red_count:
            masked = np.where(mask_red==1,red,0)
            tabletarget = table_red

        resultmusic = None
        for height in range(masked.shape[0]):
            unique, counts = np.unique(masked[height], return_counts=True)
            if len(unique) > 1:
                index = -np.argmax(np.flip(counts[1:])) - 1
                intensity = unique[index]
                bins = np.where(masked[height]==intensity, 1, 0)
                hexs = bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
                tablekey = f"{height:02d}{''.join([format(v, '0x') for v in hexs])}"
            else:
                tablekey = f'{height:02d}'
            if not tablekey in tabletarget.keys():
                break

            if type(tabletarget[tablekey]) == str:
                resultmusic = tabletarget[tablekey]
                break

            tabletarget = tabletarget[tablekey]

        if resultmusic == music:
            report.through()
            break
        else:
            report.error(f'Mismatch {key}: {resultmusic} {music}')

    report.report()

    return {
        'trim': informations_define['music']['trim'],
        'masks': {'blue': mask_blue, 'red': mask_red, 'gray': mask_gray},
        'tables': {'blue': table_blue, 'red': table_red, 'gray': table_gray},
        'musics': musics,
        'factors': factors
    }

def evaluate_musics(music):
    report = Report('resultmusic_evaluate')

    musictable = load_resource_serialized(f'musictable{define.musictable_version}', True)

    report.append_log(f"Registered count of arcade(gray color): {len(music['tables']['gray'])}")
    report.append_log(f"Registered count of infinitas(blue color): {len(music['tables']['blue'])}")
    report.append_log(f"Registered count of leggendaria(red color): {len(music['tables']['red'])}")

    def listup(list, target):
        if type(target) is str:
            list.append(target)
        else:
            for key in target.keys():
                listup(list, target[key])
    arcade_musics = []
    listup(arcade_musics, music['tables']['gray'])
    infinitas_musics = []
    listup(infinitas_musics, music['tables']['blue'])
    leggendaria_musics = []
    listup(leggendaria_musics, music['tables']['red'])

    not_exists = []
    for musicname in arcade_musics:
        if not musicname in musictable['musics'].keys():
            escaped = musicname.encode('unicode-escape').decode('UTF-8')
            not_exists.append(f'- {musicname}({escaped})')
    for musicname in infinitas_musics:
        if not musicname in musictable['musics'].keys():
            escaped = musicname.encode('unicode-escape').decode('UTF-8')
            not_exists.append(f'- {musicname}({escaped})')
    for musicname in leggendaria_musics:
        if not musicname in musictable['musics'].keys():
            escaped = musicname.encode('unicode-escape').decode('UTF-8')
            not_exists.append(f'- {musicname}({escaped})')

    not_registereds = []
    for musicname in musictable['musics'].keys():
        if not musicname in arcade_musics and not musicname in infinitas_musics:
            escaped = musicname.encode('unicode-escape').decode('UTF-8')
            not_registereds.append(f'- {musicname}({escaped})')

    musictable_leggendarias = []
    for playmode in musictable['leggendarias'].keys():
        for musicname in musictable['leggendarias'][playmode]:
            if not musicname in musictable_leggendarias:
                musictable_leggendarias.append(musicname)
    not_registereds_leggendaria = []
    for musicname in musictable_leggendarias:
        if not musicname in leggendaria_musics:
            escaped = musicname.encode('unicode-escape').decode('UTF-8')
            not_registereds_leggendaria.append(f'- {musicname}({escaped})')
    
    output = []
    output.append(f"Registered count of arcade(gray color): {len(music['tables']['gray'])}")
    output.append('')
    output.append(f"Registered count of infinitas(blue color): {len(music['tables']['blue'])}")
    output.append('')
    output.append(f"Registered count of leggendaria(red color): {len(music['tables']['red'])}")
    output.append('')


    if len(not_exists) > 0:
        report.error(f'No exists: {len(not_exists)}')
        output.append(f'No exists: {len(not_exists)}')
        output.append('')
        for line in not_exists:
            output.append(line)
        output.append(f'')
    
    if len(not_registereds) > 0:
        report.error(f'Not registered: {len(not_registereds)}')
        output.append(f'Not registered: {len(not_registereds)}')
        output.append('')
        for line in not_registereds:
            output.append(line)
        output.append(f'')
    
    if len(not_registereds_leggendaria) > 0:
        report.error(f'Not registered leggendaria: {len(not_registereds_leggendaria)}')
        output.append(f'Not registered leggendaria: {len(not_registereds_leggendaria)}')
        output.append('')
        for line in not_registereds_leggendaria:
            output.append(line)
        output.append(f'')
    
    output_filepath = join(report_basedir_musicrecog, f'register result.txt')
    with open(output_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))

    report.report()

if __name__ == '__main__':
    try:
        with open(dc.label_filepath) as f:
            labels = json.load(f)
    except Exception:
        print(f"{dc.label_filepath}を読み込めませんでした。")
        exit()
    
    informations_define = load_define()
    if informations_define is None:
        exit()

    musicshape = (
        informations_define['music']['trim'][0].stop-informations_define['music']['trim'][0].start,
        informations_define['music']['trim'][1].stop-informations_define['music']['trim'][1].start,
    )

    informations = load_informations(labels)
    
    organize(informations)

    if not exists(report_basedir_musicrecog):
        mkdir(report_basedir_musicrecog)

    play_mode = learning_playmode(informations)
    difficulty = learning_difficulty(informations)
    notes = learning_notes(informations)
    music = learning_musics(informations)
    playspeed = learning_playspeed(informations)

    evaluate_musics(music)

    filename = f'informations{define.informations_recognition_version}.res'

    data = {
        'play_mode': play_mode,
        'difficulty': difficulty,
        'notes': notes,
        'playspeed': playspeed,
        'music': music,
    }

    save_resource_serialized(filename, data, True)
