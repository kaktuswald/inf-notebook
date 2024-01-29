from PIL import Image
import json
from sys import exit
from os import mkdir
from os.path import join,isfile,exists
import numpy as np

from define import define
from image import generate_filename
import data_collection as dc
from resources_generate import Report,save_resource_serialized,registries_dirname,report_dirname
from resources_larning import larning_multivalue
from resources_generate_musictable import generate as generate_musictable

recognition_define_filename = 'define_recognition_informations.json'

arcadeallmusics_filename = 'musics_arcade_all.txt'
infinitasonlymusics_filename = 'musics_infinitas_only.txt'

report_organize_filename = 'organize.txt'
report_registered_musics_filename = 'musics_registered.txt'
report_missing_musics_filename = 'musics_missing_in_arcade.txt'

recognition_define_filepath = join(registries_dirname, recognition_define_filename)
arcadeallmusics_filepath = join(registries_dirname, arcadeallmusics_filename)
infinitasonlymusics_filepath = join(registries_dirname, infinitasonlymusics_filename)

report_basedir_musicrecog = join(report_dirname, 'musicrecog')
report_basedir_musictable = join(report_dirname, 'musictable')

musicfilenametest_basedir = join(report_dirname, 'music_filename')

class Informations():
    def __init__(self, np_value, label):
        self.np_value = np_value
        self.label = label

def load_informations(labels):
    keys = [key for key in labels.keys() if labels[key]['informations'] is not None]

    informations = {}
    for key in keys:
        filename = f'{key}.png'
        filepath = join(dc.informations_basepath, filename)
        if isfile(filepath):
            image = Image.open(filepath)
            if image.height != 78:
                continue

            np_value = np.array(image)
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
        slice(ret['difficulty']['trim'][1][0], ret['difficulty']['trim'][1][1]),
        ret['difficulty']['trim'][2]
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

    blue_lower = np.array([np.tile([[v2[0] for v2 in v1]], (width, 1)) for v1 in define['blue_thresholds']])
    blue_upper = np.array([np.tile([[v2[1] for v2 in v1]], (width, 1)) for v1 in define['blue_thresholds']])
    red_lower = np.array([np.tile([[v2[0] for v2 in v1]], (width, 1)) for v1 in define['red_thresholds']])
    red_upper = np.array([np.tile([[v2[1] for v2 in v1]], (width, 1)) for v1 in define['red_thresholds']])
    gray_lower = np.array([np.tile(v[0], (width, 3)) for v in define['gray_thresholds']])
    gray_upper = np.array([np.tile(v[1], (width, 3)) for v in define['gray_thresholds']])

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

def larning_music(targets, report, name):
    map = {}

    inspect = {}
    musicnotuniques = {}
    for music, values in targets.items():
        for key, value in values.items():
            mapkeys = []
            for height in range(value.shape[0]):
                unique, counts = np.unique(value[height], return_counts=True)
                if len(unique) == 1:
                    continue

                index = -np.argmax(np.flip(counts[1:])) - 1
                intensity = unique[index]
                bins = np.where(value[height]==intensity, 1, 0)
                hexs = bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
                mapkeys.append(f"{height:02d}{''.join([format(v, '0x') for v in hexs])}")
            
            maptarget = map
            for mapkey in mapkeys[:-1]:
                if not mapkey in maptarget:
                    maptarget[mapkey] = {}
                maptarget = maptarget[mapkey]
            maptarget[mapkeys[-1]] = music
            
            concatenatekey = ''.join(mapkeys)

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
            report.error(f'key: {tablekey})')
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

        if not 'difficulty' in label.keys() or label['difficulty'] is None:
            continue
        if not 'level' in label.keys() or label['level'] is None:
            continue
        if not 'music' in label.keys() or label['music'] is None:
            continue
        if not 'notes' in label.keys() or label['notes'] is None:
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

def check_musics(musics, report):
    with open(arcadeallmusics_filepath, 'r', encoding='utf-8') as f:
        arcade_all_musics = f.read().split('\n')

    with open(infinitasonlymusics_filepath, 'r', encoding='utf-8') as f:
        infinitas_only_musics = f.read().split('\n')

    report.append_log(f'Arcade all music count: {len(arcade_all_musics)}')
    report.append_log(f'Infinitas only music count: {len(infinitas_only_musics)}')

    duplicates = list(set(arcade_all_musics) & set(infinitas_only_musics))
    if len(duplicates) > 0:
        report.error(f"Duplicates: {','.join(duplicates)}")

    missings_alllist = sorted([music for music in musics if not music in arcade_all_musics and not music in infinitas_only_musics])
    if len(missings_alllist) > 0:
        report.error(f"Missings: {','.join(missings_alllist)}")

    missings_arcade = sorted([music for music in arcade_all_musics if not music in musics])

    missing_musics_filepath = join(report_basedir_musicrecog, report_missing_musics_filename)
    with open(missing_musics_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(missings_arcade))

def larning_playmode(informations):
    resourcename = 'playmode'

    report = Report(resourcename)

    larning_targets = {}
    evaluate_targets = {}
    for key, target in informations.items():
        if not 'play_mode' in target.label.keys():
            continue
        
        value = target.label['play_mode']
        trimmed = target.np_value[informations_define['play_mode']['trim']]
        if not value in larning_targets.keys():
            larning_targets[value] = {}
        larning_targets[value][key] = trimmed

        evaluate_targets[key] = target
    
    report.append_log(f'Source count: {len(larning_targets)}')

    table = larning_multivalue(larning_targets, report, informations_define['play_mode']['maskvalue'])
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
            report.saveimage_errorvalue(trimmed, key)
            report.error(f'Mismatch {result} {key}')

    report.report()

    return {
        'trim': informations_define['play_mode']['trim'],
        'maskvalue': informations_define['play_mode']['maskvalue'],
        'table': table
    }

def larning_difficulty(informations):
    resourcename = 'difficulty'

    report = Report(resourcename)

    evaluate_targets = {}
    table = {'difficulty': {}, 'level': {}}
    result = {}
    for key, target in informations.items():
        if not 'difficulty' in target.label.keys() or not 'level' in target.label.keys():
            continue
        
        difficulty = target.label['difficulty']
        level = target.label['level']
        
        trimmed = target.np_value[informations_define['difficulty']['trim']]

        uniques, counts = np.unique(trimmed, return_counts=True)
        difficultykey = uniques[np.argmax(counts)]
        
        if not difficultykey in table['difficulty'].keys():
            table['difficulty'][difficultykey] = difficulty
            result[difficulty] = {'log': f'difficulty {difficulty}: {difficultykey}({key})', 'levels': {}}
        
        leveltrimmed = trimmed[informations_define['difficulty']['trimlevel']].flatten()
        bins = np.where(leveltrimmed==difficultykey, 1, 0)
        hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
        levelkey = ''.join([format(v, '0x') for v in hexs])

        if not difficulty in table['level'].keys():
            table['level'][difficulty] = {}
        if not levelkey in table['level'][difficulty].keys():
            table['level'][difficulty][levelkey] = level
            result[difficulty]['levels'][level] = f'level {difficulty} {level}: {levelkey}({key})'

        evaluate_targets[key] = target

    for difficulty in define.value_list['difficulties']:
        if difficulty in result.keys():
            report.append_log(result[difficulty]['log'])
            for level in define.value_list['levels']:
                if level in result[difficulty]['levels'].keys():
                    report.append_log(result[difficulty]['levels'][level])

    
    report.append_log(f'Source count: {len(evaluate_targets)}')

    for key, target in evaluate_targets.items():
        trimmed = target.np_value[informations_define['difficulty']['trim']]

        uniques, counts = np.unique(trimmed, return_counts=True)
        difficultykey = uniques[np.argmax(counts)]

        difficulty = None
        if difficultykey in table['difficulty'].keys():
            difficulty = table['difficulty'][difficultykey]

        if difficulty != target.label['difficulty']:
            report.saveimage_errorvalue(trimmed, f'{key}.png')
            report.error(f'Mismatch difficulty {difficulty} {key}')
            continue

        leveltrimmed = trimmed[informations_define['difficulty']['trimlevel']]
        bins = np.where(leveltrimmed.flatten()==difficultykey, 1, 0)
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

def larning_notes(informations):
    resourcename = 'notes'

    report = Report(resourcename)

    evaluate_targets = {}
    table = {}
    result = {}
    for key, target in informations.items():
        if not 'notes' in target.label.keys():
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

def larning_musics(informations):
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

    table_gray = larning_music(filtered_grays, report, 'gray')
    table_blue = larning_music(filtered_blues, report, 'blue')
    table_red = larning_music(filtered_reds, report, 'red')

    musics = sorted([*targets.keys()])
    registered_musics_filepath = join(report_basedir_musicrecog, report_registered_musics_filename)
    with open(registered_musics_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(musics))
    if not exists(musicfilenametest_basedir):
        mkdir(musicfilenametest_basedir)
    for music in musics:
        filename = generate_filename(music, '').replace('jpg', 'txt')
        filepath = join(musicfilenametest_basedir, filename)
        if not exists(filepath):
            with open(filepath, 'w', encoding='UTF-8') as f:
                f.write(f'{music}\n')
                f.write(f'{music.encode("UTF-8").hex()}\n')

    check_musics(musics, report)

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
            if len(unique) == 1:
                continue

            index = -np.argmax(np.flip(counts[1:])) - 1
            intensity = unique[index]
            bins = np.where(masked[height]==intensity, 1, 0)
            hexs = bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
            tablekey = f"{height:02d}{''.join([format(v, '0x') for v in hexs])}"
            if not tablekey in tabletarget.keys():
                break

            if type(tabletarget[tablekey]) == str:
                resultmusic = tabletarget[tablekey]
                break

            tabletarget = tabletarget[tablekey]

        if resultmusic == target.label['music']:
            report.through()
            break
        else:
            report.error(f"Mismatch {key}: {resultmusic} {target.label['music']}")

    report.report()

    return {
        'trim': informations_define['music']['trim'],
        'masks': {'blue': mask_blue, 'red': mask_red, 'gray': mask_gray},
        'tables': {'blue': table_blue, 'red': table_red, 'gray': table_gray},
        'musics': musics,
        'factors': factors
    }

def analyze(informations):
    resourcename = 'analyze'

    report = Report(resourcename)

    report.append_log(f'Source count: {len(informations)}')

    table = {}
    for key, target in informations.items():
        if not 'play_mode' in target.label.keys() or target.label['play_mode'] is None:
            continue
        if not 'difficulty' in target.label.keys() or target.label['difficulty'] is None:
            continue
        if not 'level' in target.label.keys() or target.label['level'] is None:
            continue
        if not 'music' in target.label.keys() or target.label['music'] is None:
            continue
        if not 'notes' in target.label.keys() or target.label['notes'] is None:
            continue
        
        play_mode = target.label['play_mode']
        difficulty = target.label['difficulty']
        level = target.label['level']
        music = target.label['music']

        if not music in table.keys():
            table[music] = {}
            for pm in define.value_list['play_modes']:
                table[music][pm] = {}
                for df in define.value_list['difficulties']:
                    table[music][pm][df] = {}
        
        if not level in table[music][play_mode][difficulty].values():
            table[music][play_mode][difficulty][key] = level
    
    result = {}
    output = []
    for music in table.keys():
        result[music] = {}
        for play_mode in define.value_list['play_modes']:
            result[music][play_mode] = {}
        values = [music]
        for play_mode in define.value_list['play_modes']:
            for difficulty in define.value_list['difficulties']:
                if len(table[music][play_mode][difficulty]) > 1 and play_mode == 'DP':
                    if len(table[music]['SP'][difficulty]) == 1:
                        for key, value in table[music][play_mode][difficulty].items():
                            if value == table[music]['SP'][difficulty].values()[0]:
                                del table[music][play_mode][difficulty][key]
                if len(table[music][play_mode][difficulty]) == 1:
                    result[music][play_mode][difficulty] = [*table[music][play_mode][difficulty].values()][0]
                values.append([*table[music][play_mode][difficulty].values()][0] if len(table[music][play_mode][difficulty]) == 1 else '-')
                if len(table[music][play_mode][difficulty]) > 1:
                    report.error(f'{music} {play_mode} {difficulty}:')
                    for key, value in table[music][play_mode][difficulty].items():
                        report.error(f'  level {value}({key})')
        output.append(','.join(values))

    musics_analyzed_filepath = join(report_basedir_musictable, 'musics_analyzed.csv')
    with open(musics_analyzed_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))
    
    report.report()

    return result

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
        informations_define['music']['trim'][1].stop-informations_define['music']['trim'][1].start
    )

    informations = load_informations(labels)
    
    organize(informations)

    if not exists(report_basedir_musicrecog):
        mkdir(report_basedir_musicrecog)

    play_mode = larning_playmode(informations)
    difficulty = larning_difficulty(informations)
    notes = larning_notes(informations)
    music = larning_musics(informations)

    filename = f'informations{define.informations_recognition_version}.res'
    save_resource_serialized(filename, {
        'play_mode': play_mode,
        'difficulty': difficulty,
        'notes': notes,
        'music': music
    })

    if not exists(report_basedir_musictable):
        mkdir(report_basedir_musictable)
    
    analyzed_musics = analyze(informations)
    musictable = generate_musictable(analyzed_musics, report_basedir_musictable)

    filename = f'musictable{define.musictable_version}.res'
    save_resource_serialized(filename, musictable)

    if len(music['musics']) != len(musictable['musics']):
        print(f"Mismatch music count")
        print(f"recog music count: {len(music['musics'])}")
        print(f"musictable music count: {len(musictable['musics'])}")
