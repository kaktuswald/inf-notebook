from PIL import Image
import json
from sys import exit
from os import mkdir
from os.path import join,isfile,exists
import numpy as np

from define import define
from result import generate_resultfilename
import data_collection as dc
from resources_generate import Report,save_resource_serialized,report_dirname
from resources_larning import larning_multivalue

recognition_define_filename = '_define_recognition_informations.json'

arcadeallmusics_filename = 'musics_arcade_all.txt'
infinitasonlymusics_filename = 'musics_infinitas_only.txt'

report_organize_filename = 'organize.txt'
report_registered_musics_filename = 'musics_registered.txt'
report_missing_musics_filename = 'musics_missing_in_arcade.txt'

otherreport_basedir = join(report_dirname, 'informations')
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
        slice(ret['music']['trim'][1][0], ret['music']['trim'][1][1])
    )

    return ret

def filter(targets, report, bluevalue, redvalue, gray_threshold):
    result = []
    grays = {}
    blues = {}
    reds = {}
    for music, values in targets.items():
        result.append(f'{music}: {len(values)}')
        for key, value in values.items():
            blue = np.where(value[:,:,2]==bluevalue,value[:,:,2],0)
            red = np.where(value[:,:,0]==redvalue,value[:,:,0],0)
            gray1 = np.where((value[:,:,0]==value[:,:,1])&(value[:,:,0]==value[:,:,2]),value[:,:,0],0)
            gray = np.where((gray1!=255)&(gray1>gray_threshold),gray1,0)

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

    result_report_filepath = join(otherreport_basedir, 'filtertype.txt')
    with open(result_report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(result))
    
    return grays, blues, reds

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

    masks_report_filepath = join(otherreport_basedir, f'report_mask_{name}.txt')
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
                mapkeys.append(f"{y:02d}{color:02x}{''.join([format(v, '0x') for v in hexs])}")
            
            map_keys[key] = [f'{k[:2]} {k[2:4]} {k[4:]}' for k in mapkeys]

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
            for k in keys:
                not_uniques.append(f'({len(k):2}){k[0]}: {map_keys[k[0]]}')

    notuniques_report_filepath = join(otherreport_basedir, f'noteunique_{name}.txt')
    with open(notuniques_report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(not_uniques))

    for music in inspect_targets:
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

    inspectresult_report_filepath = join(otherreport_basedir, f'inspect_{name}.txt')
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
    with open(arcadeallmusics_filename, 'r', encoding='utf-8') as f:
        arcade_all_musics = f.read().split('\n')

    with open(infinitasonlymusics_filename, 'r', encoding='utf-8') as f:
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

    missing_musics_filepath = join(otherreport_basedir, report_missing_musics_filename)
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

    for music in targets.keys():
        encoded = music.encode('UTF-8').hex()
        if len(encoded) > 240:
            report.error(f'Record file name too long: {music}')

    grays, blues, reds = filter(
        targets,
        report,
        informations_define['music']['bluevalue'],
        informations_define['music']['redvalue'],
        informations_define['music']['gray_threshold']
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
    registered_musics_filepath = join(otherreport_basedir, report_registered_musics_filename)
    with open(registered_musics_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(musics))
    if not exists(musicfilenametest_basedir):
        mkdir(musicfilenametest_basedir)
    for music in musics:
        filename = generate_resultfilename(music, '').replace('jpg', 'txt')
        filepath = join(musicfilenametest_basedir, filename)
        if not exists(filepath):
            with open(filepath, 'w', encoding='UTF-8') as f:
                f.write(music)

    check_musics(musics, report)

    outputtable({'gray': table_gray, 'blue': table_blue, 'red': table_red})

    for key, target in informations.items():
        if not 'music' in target.label.keys() or target.label['music'] is None:
            continue

        trimmed = target.np_value[informations_define['music']['trim']]

        blue = np.where(trimmed[:,:,2]==informations_define['music']['bluevalue'],trimmed[:,:,2],0)
        red = np.where(trimmed[:,:,0]==informations_define['music']['redvalue'],trimmed[:,:,0],0)
        gray1 = np.where((trimmed[:,:,0]==trimmed[:,:,1])&(trimmed[:,:,0]==trimmed[:,:,2]),trimmed[:,:,0],0)
        gray = np.where((gray1!=255)&(gray1>informations_define['music']['gray_threshold']),gray1,0)

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

        for y in np.argsort(maxcounts)[::-1]:
            color = int(maxcount_values[y])
            bins = np.where(masked[y]==color, 1, 0)
            hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
            mapkey = f"{y:02d}{color:02x}{''.join([format(v, '0x') for v in hexs])}"
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
        'bluevalue': informations_define['music']['bluevalue'],
        'redvalue': informations_define['music']['redvalue'],
        'gray_threshold': informations_define['music']['gray_threshold'],
        'mask': {'blue': mask_blue, 'red': mask_red, 'gray': mask_gray},
        'table': {'blue': table_blue, 'red': table_red, 'gray': table_gray},
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

    musicshape = (
        informations_define['music']['trim'][0].stop-informations_define['music']['trim'][0].start,
        informations_define['music']['trim'][1].stop-informations_define['music']['trim'][1].start
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
