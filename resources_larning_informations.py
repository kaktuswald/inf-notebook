from PIL import Image
import json
from sys import exit
from os.path import join,isfile
import numpy as np
from scipy.stats import mode
import time

from define import define
import data_collection as dc
from resources_generate import Report,save_resource_serialized,report_dirname

recognition_define_filename = 'musics_recognition_define.json'

background_ignore_keys_filename = 'background_ignore_keys.txt'

arcadeallmusics_filename = 'musics_arcade_all.txt'
infinitasonlymusics_filename = 'musics_infinitas_only.txt'

report_backgrounds_filename = 'backgrounds.txt'
report_masks_filename = 'masks.txt'
report_notuniques_filename = 'notuniques.txt'
report_registered_musics_filename = 'musics_registered.txt'
report_missing_musics_filename = 'musics_missing_in_arcade.txt'

informations_define = {
    'version': '5.0',
    'play_mode': {
        'trim': (slice(58, 62), slice(90, 94), 1),
        'maskvalue': 255
    },
    'difficulty': {
        'trim': (slice(62, 64), slice(186, 246), 1),
        'trimlevel': (slice(0, 2), slice(52, 60)),
    },
    'notes': {
        'trim': (slice(62, 64), slice(268, 324), 1),
        'trimnumber': (slice(0, 2), slice(2, 10)),
        'maskvalue': 255,
        'digit': 4
    },
    'music': (slice(0, 10), slice(212, 272)),
    'background_key_position': (-2, 0),
    "gray_thresholds":  (220, 220, 220, 220, 220, 216, 211, 211, 211, 187)
}

shape = (
    informations_define['music'][0].stop-informations_define['music'][0].start,
    informations_define['music'][1].stop-informations_define['music'][1].start
)

otherreport_basedir = join(report_dirname, 'music')

class Informations():
    def __init__(self, np_value, label):
        self.np_value = np_value
        self.label = label

class MusicData():
    def __init__(self, np_value, background_key, music):
        self.np_value = np_value
        self.background_key = background_key
        self.music = music

def load_informations(labels):
    keys = [key for key in labels.keys() if labels[key]['informations'] is not None]

    informations = {}
    for key in keys:
        filename = f'{key}.png'
        filepath = join(dc.informations_basepath, filename)
        if isfile(filepath):
            image = Image.open(filepath)
            if image.height == 71:
                continue

            np_value = np.array(image)
            informations[key] = Informations(np_value, labels[key]['informations'])
    
    return informations

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

    background_sources = {}
    reportresult = {}
    added_musics = {}
    for key, target in targets.items():
        if key in ignore_keys:
            continue
        if not target.background_key in background_sources.keys():
            background_sources[target.background_key] = []
            added_musics[target.background_key] = []
            reportresult[target.background_key] = []
        if not target.music in added_musics[target.background_key]:
            background_sources[target.background_key].append(target.np_value)
            reportresult[target.background_key].append([key, target.music])
            added_musics[target.background_key].append(target.music)
    report.append_log(f'Background sources keycount: {len(background_sources)}')

    backgrounds = {}
    for background_key in sorted(background_sources.keys()):
        stacks = np.stack(background_sources[background_key])
        result, counts = mode(stacks, keepdims=True)
        result_background = result.reshape(shape)

        backgrounds[background_key] = result_background

        report.append_log(f'{background_key:03}: {len(background_sources[background_key])}')
        report.saveimage_value(result_background, f'_background_{background_key}.png')
    
    output = []
    for bkey in sorted(reportresult.keys()):
        for r in reportresult[bkey]:
            output.append(f'({bkey:3}){r[0]}: {r[1]}')
    
    backgrounds_report_filepath = join(otherreport_basedir, report_backgrounds_filename)
    with open(backgrounds_report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))

    return backgrounds

def filter(targets, backgrounds):
    gray_filter = np.tile(np.array(informations_define['gray_thresholds']), (shape[1], 1)).T

    filtereds = {}
    np_values = {}
    for music in targets.keys():
        filtereds[music] = {}
        for key, target in targets[music].items():
            np_values[key] = []

            np_value = target.np_value
            background_key = target.background_key
            np_values[key].append(np_value)

            background_removed = np.where(backgrounds[background_key]!=np_value, np_value, 0)
            np_values[key].append(background_removed)

            gray_filtered = np.where(background_removed>=gray_filter, background_removed, 0)
            np_values[key].append(gray_filtered)

            filtereds[music][key] = gray_filtered
    
    return filtereds, np_values

def generate_mask(backgrounds, targets, filtereds):
    mask = np.full(shape, False, dtype='bool')
    mask_report = {}
    for music in filtereds.keys():
        background_matches = []
        for key, current in filtereds[music].items():
            stacked = np.stack([np.where(current!=target, True, False) for target in filtereds[music].values()])
            result = np.any(stacked, axis=0)
            mismatch = np.where(result, targets[music][key].np_value, 0)
            background_match = np.where(mismatch==backgrounds[targets[music][key].background_key], True, False)
            background_matches.append(background_match)
        match_result = np.any(np.stack(background_matches), axis=0)
        mask = np.where(match_result, True, mask)
        mask_report[music] = np.stack(np.where(match_result)).T
    
    output = []
    for music in sorted(mask_report.keys()):
        if len(mask_report[music]) != 0:
            output.append(f"({len(targets[music]):2}:{len(mask_report[music]):2}){music}: {' '.join([str(p) for p in mask_report[music]])}")

    masks_report_filepath = join(otherreport_basedir, report_masks_filename)
    with open(masks_report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))

    return mask

def larning_music(targets, backgrounds, report):
    filtereds, np_values = filter(targets, backgrounds)

    mask = generate_mask(backgrounds, targets, filtereds)
    report.saveimage_value(mask, 'mask.png')

    map_keys = {}
    map = {}

    cnt = 0
    for music in filtereds.keys():
        for key, filtered in filtereds[music].items():
            masked = np.where(mask, 0, filtered)
            np_values[key].append(masked)

            maxcounts = []
            maxcount_values = []
            for line in masked:
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
                bins = np.where(masked[y]==color, 1, 0)
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
    print(cnt)
    inspect_targets = []

    result = {}
    optimization_report = {}
    def optimization(resulttarget, maptarget):
        if len(maptarget['musics']) >= 2:
            if len(maptarget['keys']) == 0:
                musics = [m for m in maptarget['musics'].keys()]
                print('duplicate')
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
    optimization(result, map)

    not_uniques = []
    for music, keys in [*optimization_report.items()]:
        if len(keys) >= 2:
            report.error(f'not unique: {music} {keys}')
            not_uniques.append(f'not unique: {music} {keys}')
            inspect_targets.append(music)
            not_uniques.append(f'({len(keys):2}){music}:')
            for k in keys:
                not_uniques.append(f"{' '.join(k)}")

    notuniques_report_filepath = join(otherreport_basedir, report_notuniques_filename)
    with open(notuniques_report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(not_uniques))

    print(len(inspect_targets))
    if len(inspect_targets) > 0:
        for music in inspect_targets:
            escape_music_name = music.replace('"', '')
            escape_music_name = escape_music_name.replace('/', '')
            escape_music_name = escape_music_name.replace(',', '')
            escape_music_name = escape_music_name.replace('\n', '')
            escape_music_name = escape_music_name.replace('?', '')
            escape_music_name = escape_music_name.replace('!', '')
            escape_music_name = escape_music_name.replace('*', '')
            escape_music_name = escape_music_name.replace(':', '')

            report.error(music)
            for key in targets[music].keys():
                output_name = f'{escape_music_name}_{key}'

                for index in range(len(np_values[key])):
                    report.saveimage_errorvalue(np_values[key][index], f'{output_name}_{index}.png')
                
                keylist = [(f'{target[:2]}', target[2:]) for target in map_keys[key][:6]]
                report.error(f'{key}: {keylist}')

    music_list = sorted([*targets.keys()])

    registered_musics_filepath = join(otherreport_basedir, report_registered_musics_filename)
    with open(registered_musics_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(music_list))

    return music_list, mask, result

def organize_musics(keys, labels):
    difficulties = {}
    for difficulty in define.value_list['difficulties']:
        difficulties[difficulty] = []
    levels = {}
    for level in define.value_list['levels']:
        levels[level] = []

    for key in keys:
        target = labels[key]
        if not 'informations' in target.keys() or target['informations'] is None:
            continue

        informations = target['informations']
        if not 'music' in informations.keys() or informations['music'] is None:
            continue

        music = informations['music']
        if 'difficulty' in informations.keys() and informations['difficulty'] in define.value_list['difficulties']:
            difficulty = informations['difficulty']
            if not music in difficulties[difficulty]:
                difficulties[difficulty].append(music)
        if 'level' in informations.keys() and informations['level'] in define.value_list['levels']:
            level = informations['level']
            if not music in levels[level]:
                levels[level].append(music)
    
    for key, value in difficulties.items():
        print(key, len(value))
    for key, value in levels.items():
        print(key, len(value))

    return difficulties, levels

def check(target, arcade_all_musics, infinitas_only_musics):
    if type(target) is dict:
        for value in target.values():
            check(value, arcade_all_musics, infinitas_only_musics)
    else:
        if target is not None and not target in arcade_all_musics and not target in infinitas_only_musics:
            print(f"not found: {target}({target.encode('unicode-escape').decode()})")

def check_musics(musics, recog_musics, report):
    with open(arcadeallmusics_filename, 'r', encoding='utf-8') as f:
        arcade_all_musics = f.read().split('\n')

    with open(infinitasonlymusics_filename, 'r', encoding='utf-8') as f:
        infinitas_only_musics = f.read().split('\n')

    report.append_log(f'arcade all music count: {len(arcade_all_musics)}')
    report.append_log(f'infinitas only music count: {len(infinitas_only_musics)}')

    duplicates = list(set(arcade_all_musics) & set(infinitas_only_musics))
    if len(duplicates) > 0:
        report.append_log(f"duplicates: {','.join(duplicates)}")

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
    
    report.append_log(f'source count: {len(larning_targets)}')

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
            report.append_log(f'difficulty {difficulty}: {difficultykey}({key})')
        
        leveltrimmed = trimmed[informations_define['difficulty']['trimlevel']].flatten()
        bins = np.where(leveltrimmed==difficultykey, 1, 0)
        hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
        levelkey = ''.join([format(v, '0x') for v in hexs])

        if not difficulty in table['level'].keys():
            table['level'][difficulty] = {}
        if not levelkey in table['level'][difficulty].keys():
            table['level'][difficulty][levelkey] = level
            report.append_log(f'level {difficulty} {level}: {levelkey}({key})')

        evaluate_targets[key] = target
    
    report.append_log(f'source count: {len(evaluate_targets)}')
    # print(table)

    report.append_log(f"difficulty key count: {len(table['difficulty'].keys())}")
    for difficulty in table['difficulty'].values():
        report.append_log(f"{difficulty} level key count: {len(table['level'][difficulty].keys())}")

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
                report.append_log(f'{value % 10}: {tablekey}')
                report.saveimage_value(trimmed_once, f'{value % 10}-{key}.png')

            value = value // 10
            pos -= 1

        evaluate_targets[key] = target
    
    report.append_log(f'key count: {len(table)}')

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

    report.append_log(f'file count: {len(informations)}')

    background_key_position = informations_define['background_key_position']
    targets = {}
    for key, target in informations.items():
        if not 'music' in target.label.keys() or target.label['music'] is None:
            continue

        targets[key] = MusicData(
            target.np_value[informations_define['music']],
            target.np_value[background_key_position],
            target.label['music']
        )
    
    backgrounds = generate_backgrounds(targets, report)

    data_musics = {}
    for key, target in targets.items():
        if not target.music in data_musics.keys():
            data_musics[target.music] = {}
        data_musics[target.music][key] = target

    report.append_log(f'Music count: {len(data_musics)}')

    start = time.time()
    musics, mask, recog_musics = larning_music(data_musics, backgrounds, report)
    print(f'time: {time.time() - start}')

    check_musics(musics, recog_musics, report)
    print('top', len(recog_musics))

    for music in musics:
        encoded = music.encode('UTF-8').hex()
        if len(encoded) > 240:
            report.error(f'Record file name too long: {music}')

    report.report()

    return {
        'define': informations_define,
        'backgrounds': backgrounds,
        'mask': mask,
        'recognition': recog_musics,
        'musics': musics
    }

if __name__ == '__main__':
    try:
        with open(dc.label_filepath) as f:
            labels = json.load(f)
    except Exception:
        print(f"{dc.label_filepath}を読み込めませんでした。")
        exit()
    
    informations = load_informations(labels)
    
    play_mode = larning_playmode(informations)
    difficulty = larning_difficulty(informations)
    notes = larning_notes(informations)
    # music = larning_musics(informations)

    save_resource_serialized('informations.res', {
        'play_mode': play_mode,
        'difficulty': difficulty,
        'notes': notes
        # 'music': music
    })
