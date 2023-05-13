from PIL import Image
import json
from sys import exit
from os.path import join,isfile
import numpy as np
from scipy.stats import mode

from define import define
import data_collection as dc
from resources_generate import Report,save_resource_serialized,report_dirname

recognition_define_filename = '_define_recognition_informations.json'

background_ignore_keys_filename = 'background_ignore_keys.txt'

arcadeallmusics_filename = 'musics_arcade_all.txt'
infinitasonlymusics_filename = 'musics_infinitas_only.txt'

report_organize_filename = 'organize.txt'
report_backgrounds_filename = 'backgrounds.txt'
report_masks_filename = 'masks.txt'
report_notuniques_filename = 'notuniques.txt'
report_inspectresult_filename = 'inspect.txt'
report_registered_musics_filename = 'musics_registered.txt'
report_missing_musics_filename = 'musics_missing_in_arcade.txt'

otherreport_basedir = join(report_dirname, 'music')

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
        with open(recognition_define_filename) as f:
            ret = json.load(f)
    except Exception:
        print(f"{recognition_define_filename}を読み込めませんでした。")
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
        slice(ret['music']['trim'][1][0], ret['music']['trim'][1][1]),
        ret['music']['trim'][2]
    )
    ret['music']['background_key_position'] = tuple(ret['music']['background_key_position'])
    ret['music']['maptrim'] = (
        slice(ret['music']['maptrim'][0][0], ret['music']['maptrim'][0][1]),
        slice(ret['music']['maptrim'][1][0], ret['music']['maptrim'][1][1])
    )
    ret['music']['brightness_thresholds'] = tuple(ret['music']['brightness_thresholds'])

    return ret

def larning_multivalue(targets, report):
    if len(targets) == 0:
        report.append_log('count: 0')
        return None

    table = {}
    for value in targets.keys():
        keys = []
        for key, np_value in targets[value].items():
            bins = np.where(np_value.flatten()==informations_define['play_mode']['maskvalue'], 1, 0)
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

def generate_backgrounds(targets, report):
    ignore_keys_filepath = join(dc.collection_basepath, background_ignore_keys_filename)
    if isfile(ignore_keys_filepath):
        with open(ignore_keys_filepath, 'r', encoding='utf-8') as f:
            ignore_keys = f.read().split('\n')
    else:
        ignore_keys = []
    report.append_log(f'Ignore key count: {len(ignore_keys)}')

    report.append_log('generate backgrounds')

    background_sources = {}
    reportresult = {}
    added_musics = {}
    for music, values in targets.items():
        for key, value in values.items():
            if key in ignore_keys:
                continue

            background_key = value[informations_define['music']['background_key_position']]
            if not background_key in background_sources.keys():
                background_sources[background_key] = []
                added_musics[background_key] = []
                reportresult[background_key] = []
            if not music in added_musics[background_key]:
                background_sources[background_key].append(value)
                reportresult[background_key].append([key, music])
                added_musics[background_key].append(music)
    report.append_log(f'Background sources keycount: {len(background_sources)}')

    backgrounds = {}
    for background_key in sorted(background_sources.keys()):
        stacks = np.stack(background_sources[background_key])
        result, counts = mode(stacks, keepdims=True)
        result_background = result.reshape(backgroundshape)

        backgrounds[background_key] = result_background

        report.append_log(f'{background_key:03}: {len(background_sources[background_key])}')
        report.saveimage_value(result_background, f'__background_{background_key}.png')
    
    output = []
    for bkey in sorted(reportresult.keys()):
        for r in reportresult[bkey]:
            output.append(f'({bkey:3}){r[0]}: {r[1]}')
    
    backgrounds_report_filepath = join(otherreport_basedir, report_backgrounds_filename)
    with open(backgrounds_report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))
    
    return backgrounds

def generate_mask(targets, backgrounds, report):
    report.append_log('Generate mask')

    mask = np.full(backgroundshape, 0)
    mask_report = {}
    for music, values in targets.items():
        background_matches = []
        for key, value in values.items():
            stacked = np.stack([np.where(value!=target, 1, 0) for target in values.values()])
            result = np.any(stacked, axis=0)
            mismatch = np.where(result, values[key], 0)
            background_key = value[informations_define['music']['background_key_position']]
            background_match = np.where(mismatch==backgrounds[background_key], 1, 0)
            background_matches.append(background_match)
        match_result = np.any(np.stack(background_matches), axis=0)
        mask = np.where(match_result, 1, mask)
        mask_report[music] = np.stack(np.where(match_result)).T
    report.append_log(f'Mask pixel count: {np.count_nonzero(mask)}')
    
    output = []
    for music in sorted(mask_report.keys()):
        if len(mask_report[music]) != 0:
            output.append(f"({len(targets[music]):2}:{len(mask_report[music]):3}){music}: {' '.join([str(p) for p in mask_report[music]])}")

    masks_report_filepath = join(otherreport_basedir, report_masks_filename)
    with open(masks_report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))

    report.saveimage_value(np.where(mask==1,True,False), 'mask.png')

    return mask

def filter_background(targets, backgrounds):
    for values in targets.values():
        for key, value in values.items():
            background_key = value[informations_define['music']['background_key_position']]
            values[key] = np.where(value!=backgrounds[background_key], value, 0)

def filter_mask(targets, mask):
    for values in targets.values():
        for key, value in values.items():
            values[key] = np.where(mask==1,value,0)

def trimming_maptrim(targets):
    for values in targets.values():
        for key, value in values.items():
            values[key] = value[informations_define['music']['maptrim']]

def filter_brightness(targets):
    brightness_filter = np.tile(np.array(informations_define['music']['brightness_thresholds']), (mapareashape[1], 1)).T

    for items in targets.values():
        for key, value in items.items():
            items[key] = np.where(value>=brightness_filter, value, 0)
    
    return brightness_filter

def larning_music(targets, report):
    map_keys = {}
    map = {}

    for music, values in targets.items():
        for key, value in values.items():
            maxcounts = []
            maxcount_values = []
            for line in value:
                unique, counts = np.unique(line, return_counts=True)
                if len(counts) != 1:
                    index = -np.argmax(np.flip(counts[1:])) - 1
                    maxcounts.append(counts[index])
                    maxcount_values.append(unique[index])
                else:
                    maxcounts.append(0)
                    maxcount_values.append(0)

            mapkeys = []
            for y in np.argsort(maxcounts)[::-1]:
                color = int(maxcount_values[y])
                bins = np.where(value[y]==color, 1, 0)
                hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
                mapkeys.append(f"{y:02d}{''.join([format(v, '0x') for v in hexs])}")
            
            map_keys[key] = mapkeys

            target = map
            for k in mapkeys:
                if len(target) == 0:
                    target['musics'] = {}
                    target['keys'] = {}

                if not music in target['musics'].keys():
                    target['musics'][music] = []
                target['musics'][music].append(key)

                if not k in target['keys'].keys():
                    target['keys'][k] = {}
                target = target['keys'][k]
            if len(target) == 0:
                target['musics'] = {}
                target['keys'] = {}

            if not music in target['musics'].keys():
                target['musics'][music] = []
            target['musics'][music].append(key)
    inspect_targets = []

    result = {}
    optimization_report = {}
    def optimization(resulttarget, maptarget):
        if len(maptarget['musics']) >= 2:
            if len(maptarget['keys']) == 0:
                musics = [m for m in maptarget['musics'].keys()]
                report.error(f'duplicate: {musics}')
                for m in musics:
                    report.error(f"{m}: {maptarget['musics'][m]}")
                inspect_targets.extend(musics)
            else:
                for key in maptarget['keys'].keys():
                    resulttarget[key] = {}
                    music = optimization(resulttarget[key], maptarget['keys'][key])
                    if music is not None:
                        resulttarget[key] = music
            return None
        else:
            music = [*maptarget['musics'].keys()][0]
            music_keys = maptarget['musics'].values()
            resulttarget = music
            if not music in optimization_report.keys():
                optimization_report[music] = []
            optimization_report[music].append(*music_keys)

            return music
    if len(map) >= 1:
        optimization(result, map)

    not_uniques = []
    for music, keys in [*optimization_report.items()]:
        if len(keys) >= 2:
            not_uniques.append(f'not unique: {music} {keys}')
            inspect_targets.append(music)
            not_uniques.append(f'({len(keys):2}){music}:')
            for k in keys:
                not_uniques.append(f"{' '.join(k)}")

    notuniques_report_filepath = join(otherreport_basedir, report_notuniques_filename)
    with open(notuniques_report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(not_uniques))

    inspect_result = []
    for music in targets.keys():
        inspect_result.append(f'music: {music}')
        escape_music_name = music.replace('"', '')
        escape_music_name = escape_music_name.replace('/', '')
        escape_music_name = escape_music_name.replace(',', '')
        escape_music_name = escape_music_name.replace('\n', '')
        escape_music_name = escape_music_name.replace('?', '')
        escape_music_name = escape_music_name.replace('!', '')
        escape_music_name = escape_music_name.replace('*', '')
        escape_music_name = escape_music_name.replace(':', '')

        for key, value in targets[music].items():
            report.saveimage_errorvalue(value, f'_{escape_music_name}_{key}.png')
            inspect_result.append(f'{key}: {map_keys[key]}')

    inspectresult_report_filepath = join(otherreport_basedir, report_inspectresult_filename)
    with open(inspectresult_report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(inspect_result))

    return result

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

        difficulty = label['difficulty']
        level = label['level']
        music = label['music']

        if not music in result.keys():
            result[music] = {}
        
        result[music][difficulty] = level

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
        for difficulty, level in values.items():
            output.append(f'{music}: {difficulty} {level}')

    report_filepath = join(report_dirname, report_organize_filename)
    with open(report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))

def check_musics(musics, recog_musics, report):
    with open(arcadeallmusics_filename, 'r', encoding='utf-8') as f:
        arcade_all_musics = f.read().split('\n')

    with open(infinitasonlymusics_filename, 'r', encoding='utf-8') as f:
        infinitas_only_musics = f.read().split('\n')

    report.append_log(f'Arcade all music count: {len(arcade_all_musics)}')
    report.append_log(f'Infinitas only music count: {len(infinitas_only_musics)}')

    duplicates = list(set(arcade_all_musics) & set(infinitas_only_musics))
    if len(duplicates) > 0:
        report.append_log(f"Duplicates: {','.join(duplicates)}")

    def check(target, arcade_all_musics, infinitas_only_musics):
        if type(target) is dict:
            for value in target.values():
                check(value, arcade_all_musics, infinitas_only_musics)
        else:
            if target is not None and not target in arcade_all_musics and not target in infinitas_only_musics:
                report.error(f"Not found: {target}({target.encode('unicode-escape').decode()})")

    check(recog_musics, arcade_all_musics, infinitas_only_musics)

    result = sorted([music for music in arcade_all_musics if not music in musics])

    missing_musics_filepath = join(otherreport_basedir, report_missing_musics_filename)
    with open(missing_musics_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(result))

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

    table = larning_multivalue(larning_targets, report)
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
    resourcename = 'music'

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

    backgrounds = generate_backgrounds(targets, report)
    mask = generate_mask(targets, backgrounds, report)

    filter_background(targets, backgrounds)
    filter_mask(targets, mask)
    trimming_maptrim(targets)
    brightness_filter = filter_brightness(targets)

    table = larning_music(targets, report)

    musics = sorted([*targets.keys()])
    registered_musics_filepath = join(otherreport_basedir, report_registered_musics_filename)
    with open(registered_musics_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(musics))

    check_musics(musics, table, report)

    for music in targets.keys():
        encoded = music.encode('UTF-8').hex()
        if len(encoded) > 240:
            report.error(f'Record file name too long: {music}')

    for key, target in informations.items():
        if not 'music' in target.label.keys() or target.label['music'] is None:
            continue

        trimmed = target.np_value[informations_define['music']['trim']]
        background_key = trimmed[informations_define['music']['background_key_position']]
        if not background_key in backgrounds.keys():
            report.error(f'Recognition failure {key}: mismatch background key {background_key}')
            continue
        
        filtered_background = np.where(trimmed!=backgrounds[background_key], trimmed, 0)
        filtered_mask = np.where(mask==1, filtered_background, 0)

        maptrimmed = filtered_mask[informations_define['music']['maptrim']]
        filtered_brightness = np.where(maptrimmed>=brightness_filter, maptrimmed, 0)

        maxcounts = []
        maxcount_values = []
        for line in filtered_brightness:
            unique, counts = np.unique(line, return_counts=True)
            if len(counts) != 1:
                index = -np.argmax(np.flip(counts[1:])) - 1
                maxcounts.append(counts[index])
                maxcount_values.append(unique[index])
            else:
                maxcounts.append(0)
                maxcount_values.append(0)

        tabletarget = table
        for y in np.argsort(maxcounts)[::-1]:
            color = int(maxcount_values[y])
            bins = np.where(filtered_brightness[y]==color, 1, 0)
            hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
            mapkey = f"{y:02d}{''.join([format(v, '0x') for v in hexs])}"
            if not mapkey in tabletarget:
                report.error(f"Recognition failure {target.label['music']}: {key}({mapkey})")
                break
            if type(tabletarget[mapkey]) == str:
                if tabletarget[mapkey] == target.label['music']:
                    report.through()
                    break
                else:
                    report.error(f"Mismatch {key}: {tabletarget[mapkey]} {target.label['music']}")
            tabletarget = tabletarget[mapkey]

    report.report()

    return {
        'trim': informations_define['music']['trim'],
        'background_key_position': informations_define['music']['background_key_position'],
        'maptrim': informations_define['music']['maptrim'],
        'brightness_thresholds': informations_define['music']['brightness_thresholds'],
        'backgrounds': backgrounds,
        'mask': mask,
        'table': table,
        'musics': musics
    }

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

    backgroundshape = (
        informations_define['music']['trim'][0].stop-informations_define['music']['trim'][0].start,
        informations_define['music']['trim'][1].stop-informations_define['music']['trim'][1].start
    )

    mapareashape = (
        informations_define['music']['maptrim'][0].stop-informations_define['music']['maptrim'][0].start,
        informations_define['music']['maptrim'][1].stop-informations_define['music']['maptrim'][1].start
    )

    informations = load_informations(labels)
    
    organize(informations)

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
