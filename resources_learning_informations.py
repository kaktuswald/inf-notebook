import json
from sys import exit
from os.path import join,isfile

from PIL import Image
import numpy as np
from numpy import array

from define import define
import data_collection as dc
from resources import load_resource_serialized
from resources_generate import Report,save_resource_serialized,registries_dirname,report_dirname
from resources_learning import learning_multivaluemask

recognition_define_filename = 'define_recognition_informations.json'

recognition_define_filepath = join(registries_dirname, recognition_define_filename)

class Informations():
    def __init__(self, np_value, label):
        self.np_value = np_value
        self.label = label

def load_informations(labels:dict) -> dict:
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

def load_define() -> dict:
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

def organize(informations:dict, report:Report):
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
    output.append(f'Song count: {len(result)}')
    for key, value in difficulties.items():
        output.append(f'{key}: {len(value)}')
    for key, value in levels.items():
        output.append(f'{key}: {len(value)}')
    for music, values in result.items():
        for difficulty, values in values.items():
            output.append(f'{music}: {difficulty} {values[0]} {values[1]}')

    report.output_list(output, 'organize.txt')

def learning_playmode(informations:dict) -> dict:
    resourcename = 'playmode'

    report_playmode = Report(resourcename)

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
    
    report_playmode.append_log(f'Source count: {len(learning_targets)}')

    table = learning_multivaluemask(learning_targets, report_playmode, informations_define['play_mode']['maskvalue'])
    if table is None:
        report_playmode.report_playmode()
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
            report_playmode.through()
        else:
            report_playmode.saveimage_errorvalue(trimmed, f'{key}.png')
            report_playmode.error(f'Mismatch {result} {key}')

    report_playmode.report()

    if not report_playmode.count_error:
        report.through()
    else:
        report.error('Error playmode')

    return {
        'trim': informations_define['play_mode']['trim'],
        'maskvalue': informations_define['play_mode']['maskvalue'],
        'table': table
    }

def learning_difficulty(informations:dict) -> dict:
    resourcename = 'difficulty'

    report_difficulty = Report(resourcename)

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
        report_difficulty.error(f'Duplicate difficulty key')
        for key, difficulty in table['difficulty'].items():
            report_difficulty.error(f'{key}: {difficulty}')

    for difficulty in define.value_list['difficulties']:
        if difficulty in result.keys():
            report_difficulty.append_log(result[difficulty]['log'])
            for level in define.value_list['levels']:
                if level in result[difficulty]['levels'].keys():
                    report_difficulty.append_log(result[difficulty]['levels'][level])

    report_difficulty.append_log(f'Source count: {len(evaluate_targets)}')

    for key, target in evaluate_targets.items():
        trimmed = target.np_value[informations_define['difficulty']['trim']].astype(np.uint32)
        converted = trimmed[:,:,0]*0x10000+trimmed[:,:,1]*0x100+trimmed[:,:,2]

        uniques, counts = np.unique(converted, return_counts=True)
        difficultykey = uniques[np.argmax(counts)]

        difficulty = None
        if difficultykey in table['difficulty'].keys():
            difficulty = table['difficulty'][difficultykey]

        if difficulty != target.label['difficulty']:
            report_difficulty.saveimage_errorvalue(converted, f'{key}.png')
            report_difficulty.error(f'Mismatch difficulty {difficulty} {key}')
            continue

        leveltrimmed = converted[informations_define['difficulty']['trimlevel']].flatten()
        bins = np.where(leveltrimmed==difficultykey, 1, 0)
        hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
        levelkey = ''.join([format(v, '0x') for v in hexs])

        level = None
        if levelkey in table['level'][difficulty].keys():
            level = table['level'][difficulty][levelkey]

        if level != target.label['level']:
            report_difficulty.saveimage_errorvalue(trimmed, f'{key}.png')
            report_difficulty.error(f"Mismatch level {difficulty} {level} {target.label['level']} {levelkey} {key}")
            continue

        report_difficulty.through()

    report_difficulty.report()

    if not report_difficulty.count_error:
        report.through()
    else:
        report.error('Error difficulty')

    return {
        'trim': informations_define['difficulty']['trim'],
        'trimlevel': informations_define['difficulty']['trimlevel'],
        'table': table
    }

def learning_notes(informations:dict) -> dict:
    resourcename = 'notes'

    report_notes = Report(resourcename)

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
                report_notes.saveimage_value(trimmed_once, f'{value % 10}-{key}.png')

            value = value // 10
            pos -= 1

        evaluate_targets[key] = target
    
    report_notes.append_log(f'key count: {len(table)}')
    for key in sorted(result.keys()):
        report_notes.append_log(result[key])

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
            report_notes.through()
        else:
            report_notes.saveimage_errorvalue(trimmed, f'{key}.png')
            report_notes.error(f"Mismatch {value} {target.label['notes']} {key}")

    report_notes.report()

    if not report_notes.count_error:
        report.through()
    else:
        report.error('Error notes')
    
    return {
        'trim': informations_define['notes']['trim'],
        'trimnumber': informations_define['notes']['trimnumber'],
        'maskvalue': informations_define['notes']['maskvalue'],
        'digit': informations_define['notes']['digit'],
        'table': table
    }

def learning_playspeed(informations:dict) -> dict:
    resourcename = 'playspeed'

    report_playspeed = Report(resourcename)

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
    
    report_playspeed.append_log(f'Source count: {len(learning_targets)}')

    table = learning_multivaluemask(learning_targets, report_playspeed, informations_define['playspeed']['maskvalue'])
    if table is None:
        report_playspeed.report_playspeed()
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
            report_playspeed.through()
        else:
            report_playspeed.saveimage_errorvalue(trimmed, f'{key}.png')
            report_playspeed.error(f'Mismatch {result} {key}')

    report_playspeed.report()

    if not report_playspeed.count_error:
        report.through()
    else:
        report.error('Error playspeed')
    
    return {
        'trim': informations_define['playspeed']['trim'],
        'maskvalue': informations_define['playspeed']['maskvalue'],
        'table': table,
    }

def learning_songname(informations:dict) -> dict:
    resourcename = 'informations_songname'

    report_songname = Report(resourcename)

    report_songname.append_log(f'File count: {len(informations)}')

    targets = {}
    count = 0
    for key, target in informations.items():
        if not 'music' in target.label.keys() or target.label['music'] is None:
            continue

        if not target.label['music'] in targets.keys():
            targets[target.label['music']] = {}
        targets[target.label['music']][key] = target.np_value[informations_define['music']['trim']]
        count += 1
    
    report_songname.append_log(f'Source count: {count}')
    report_songname.append_log(f'Music count: {len(targets)}')

    for music in targets.keys():
        encoded = music.encode('utf-8').hex()
        if len(encoded) > 240:
            report_songname.error(f'Record file name too long: {music}')

    grays, blues, reds, factors = learning_songname_filter(
        targets,
        report_songname,
        informations_define['music']
    )
    
    mask_gray = learning_songname_generatemask(grays, report_songname, 'gray')
    mask_blue = learning_songname_generatemask(blues, report_songname, 'blue')
    mask_red = learning_songname_generatemask(reds, report_songname, 'red')

    filtered_grays = learning_songname_filtermask(grays, mask_gray)
    filtered_blues = learning_songname_filtermask(blues, mask_blue)
    filtered_reds = learning_songname_filtermask(reds, mask_red)

    table_gray = learning_songname_learning(filtered_grays, report_songname, 'gray')
    table_blue = learning_songname_learning(filtered_blues, report_songname, 'blue')
    table_red = learning_songname_learning(filtered_reds, report_songname, 'red')

    songnames = sorted([*targets.keys()])

    learning_songname_outputtable({'gray': table_gray, 'blue': table_blue, 'red': table_red}, report_songname)

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
            report_songname.through()
            break
        else:
            report_songname.error(f'Mismatch {key}: {resultmusic} {music}')
    
    report_songname.report()

    if not report_songname.count_error:
        report.through()
    else:
        report.error('Error songname')

    return {
        'trim': informations_define['music']['trim'],
        'masks': {'blue': mask_blue, 'red': mask_red, 'gray': mask_gray},
        'tables': {'blue': table_blue, 'red': table_red, 'gray': table_gray},
        'musics': songnames,
        'factors': factors
    }

def learning_songname_filter(targets:dict, report:Report, define:dict) -> (dict,dict,dict,dict,):
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

    result = []
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

    report.output_list(result, 'filtertype.txt')
    
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

def learning_songname_generatemask(targets:dict, report:Report, name:str) -> array:
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

    report.output_list(output, f'report_mask_{name}.txt')

    report.saveimage_value(np.where(mask==0,False,True), f'mask_{name}.png')

    return mask

def learning_songname_filtermask(targets:dict, mask) -> dict:
    mask_filtereds = {}
    for music, values in targets.items():
        mask_filtereds[music] = {}
        for key, value in values.items():
            mask_filtereds[music][key] = np.where(mask==1,value,0)
    
    return mask_filtereds

def learning_songname_learning(targets:dict, report:Report, name:str) -> dict:
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

    report.output_list(report_inspect, f'inspect_{name}.txt')

    report_notuniques = []
    for music, values in musicnotuniques.items():
        setted = set(values.keys())
        count = len(setted)
        if count >= 2:
            report_notuniques.append(f'not unique: {music}({count})')
            for tablekey, item in values.items():
                report_notuniques.append(f"  {tablekey}: {item['key']}")
                report.saveimage_errorvalue(item['value'], f"_{item['key']}.png")

    report.output_list(report_notuniques, f'noteunique_{name}.txt')

    return map

def learning_songname_outputtable(table:dict, report:Report):
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

    report.output_json(output, 'output.json')

def evaluate_songname(recognition:dict):
    report_songnameevaluate = Report('informations_songname_evaluate')

    musictable = load_resource_serialized(f'musictable{define.musictable_version}', True)

    report_songnameevaluate.append_log(f"Registered count of arcade(gray color): {len(recognition['tables']['gray'])}")
    report_songnameevaluate.append_log(f"Registered count of infinitas(blue color): {len(recognition['tables']['blue'])}")
    report_songnameevaluate.append_log(f"Registered count of leggendaria(red color): {len(recognition['tables']['red'])}")

    def listup(list, target):
        if type(target) is str:
            list.append(target)
        else:
            for key in target.keys():
                listup(list, target[key])
    
    arcade_songnames = []
    listup(arcade_songnames, recognition['tables']['gray'])
    infinitas_songnames = []
    listup(infinitas_songnames, recognition['tables']['blue'])
    leggendaria_songnames = []
    listup(leggendaria_songnames, recognition['tables']['red'])

    not_exists = []
    for songname in arcade_songnames:
        if not songname in musictable['musics'].keys():
            escaped = songname.encode('unicode-escape').decode('utf-8')
            not_exists.append(f'- {songname}({escaped})')
    for songname in infinitas_songnames:
        if not songname in musictable['musics'].keys():
            escaped = songname.encode('unicode-escape').decode('utf-8')
            not_exists.append(f'- {songname}({escaped})')
    for songname in leggendaria_songnames:
        if not songname in musictable['musics'].keys():
            escaped = songname.encode('unicode-escape').decode('utf-8')
            not_exists.append(f'- {songname}({escaped})')

    not_registereds = []
    for songname in musictable['musics'].keys():
        if not songname in arcade_songnames and not songname in infinitas_songnames:
            escaped = songname.encode('unicode-escape').decode('utf-8')
            not_registereds.append(f'- {songname}({escaped})')

    musictable_leggendarias = []
    for playmode in musictable['leggendarias'].keys():
        for songname in musictable['leggendarias'][playmode]:
            if not songname in musictable_leggendarias:
                musictable_leggendarias.append(songname)
    not_registereds_leggendaria = []
    for songname in musictable_leggendarias:
        if not songname in leggendaria_songnames:
            escaped = songname.encode('unicode-escape').decode('utf-8')
            not_registereds_leggendaria.append(f'- {songname}({escaped})')
    
    output = []
    output.append(f"Registered count of arcade(gray color): {len(recognition['tables']['gray'])}")
    output.append('')
    output.append(f"Registered count of infinitas(blue color): {len(recognition['tables']['blue'])}")
    output.append('')
    output.append(f"Registered count of leggendaria(red color): {len(recognition['tables']['red'])}")
    output.append('')

    if len(not_exists) > 0:
        report_songnameevaluate.error(f'No exists: {len(not_exists)}')
        output.append(f'No exists: {len(not_exists)}')
        output.append('')
        for line in not_exists:
            output.append(line)
        output.append(f'')
    
    if len(not_registereds) > 0:
        report_songnameevaluate.error(f'Not registered: {len(not_registereds)}')
        output.append(f'Not registered: {len(not_registereds)}')
        output.append('')
        for line in not_registereds:
            output.append(line)
        output.append(f'')
    
    if len(not_registereds_leggendaria) > 0:
        report_songnameevaluate.error(f'Not registered leggendaria: {len(not_registereds_leggendaria)}')
        output.append(f'Not registered leggendaria: {len(not_registereds_leggendaria)}')
        output.append('')
        for line in not_registereds_leggendaria:
            output.append(line)
        output.append(f'')
    
    report_songnameevaluate.output_list(output, 'register result.txt')

    report_songnameevaluate.report()
    
    if not report_songnameevaluate.count_error:
        report.through()
    else:
        report.error('Error songnameevaluate')

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
    
    report = Report('informations')
    
    organize(informations, report)

    play_mode = learning_playmode(informations)
    difficulty = learning_difficulty(informations)
    notes = learning_notes(informations)
    songname = learning_songname(informations)
    playspeed = learning_playspeed(informations)

    evaluate_songname(songname)

    filename = f'informations{define.informations_recognition_version}.res'

    data = {
        'play_mode': play_mode,
        'difficulty': difficulty,
        'notes': notes,
        'playspeed': playspeed,
        'music': songname,
    }

    save_resource_serialized(filename, data, True)
    
    report.report()
