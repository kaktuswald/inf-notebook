from PIL import Image
import json
from sys import exit
from os.path import join,isfile
import numpy as np

from define import define
from data_collection import collection_basepath
from resources import load_resource_serialized
from resources_generate import Report,save_resource_serialized,registries_dirname,report_dirname
from resources_larning import larning_multivalue

images_musicselect_basepath = join(collection_basepath, 'musicselect')
label_filepath = join(collection_basepath, 'label_musicselect.json')

recognition_define_filename = 'define_recognition_musicselect.json'
recognition_define_filepath = join(registries_dirname, recognition_define_filename)

report_basedir_musicrecog = join(report_dirname, 'musicrecog')

musicname_output_dirpath = join(report_dirname, 'musicselect_musicname')

class ImageValues():
    def __init__(self, np_value, label):
        self.np_value = np_value
        self.label = label

def load_images(labels):
    keys = [key for key in labels.keys()]

    imagevaleus = {}
    for filename in keys:
        filepath = join(images_musicselect_basepath, filename)
        if isfile(filepath):
            np_value = np.array(Image.open(filepath))
            imagevaleus[filename] = ImageValues(np_value, labels[filename])
    
    return imagevaleus

def load_define():
    try:
        with open(recognition_define_filepath) as f:
            ret = json.load(f)
    except Exception:
        print(f"{recognition_define_filepath}を読み込めませんでした。")
        return None
    
    return ret

def larning_playmode():
    report = Report('musicselect_playmode')

    define_target = musicselect_define['playmode']

    trim = (
        slice(define_target['trim'][0][0], define_target['trim'][0][1]),
        slice(define_target['trim'][1][0], define_target['trim'][1][1]),
        define_target['trim'][2]
    )
    maskvalue = define_target['maskvalue']

    larning_targets = {}
    evaluate_targets = {}
    for key, target in imagevalues.items():
        if not 'playmode' in target.label.keys() or target.label['playmode'] == '':
            continue
        
        value = target.label['playmode']
        trimmed = target.np_value[trim]
        if not value in larning_targets.keys():
            larning_targets[value] = {}
        larning_targets[value][key] = trimmed

        evaluate_targets[key] = target
    
    report.append_log(f'Source count: {len(larning_targets)}')

    table = larning_multivalue(larning_targets, report, maskvalue)
    if table is None:
        report.report()
        return

    for key, target in evaluate_targets.items():
        trimmed = target.np_value[trim].flatten()
        bins = np.where(trimmed==maskvalue, 1, 0)
        hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
        tablekey = ''.join([format(v, '0x') for v in hexs])

        result = None
        if tablekey in table.keys():
            result = table[tablekey]
        
        if result == target.label['playmode']:
            report.through()
        else:
            report.saveimage_errorvalue(trimmed, key)
            report.error(f'Mismatch {result} {key}')

    resource['playmode'] = {
        'trim': trim,
        'maskvalue': maskvalue,
        'table': table
    }

    report.report()

def larning_levels():
    report = Report(f'musicselect_levels')

    selectstatus = ['select', 'noselect']
    difficulties = ['beginner', 'normal', 'hyper', 'another', 'leggendaria']

    resource['levels'] = {}
    targets = {}
    for selectstate in selectstatus:
        targets[selectstate] = {}
        resource['levels'][selectstate] = {}
        for difficulty in difficulties:
            targets[selectstate][difficulty] = {}
            resource['levels'][selectstate][difficulty] = {}

    evaluate_targets = {}
    for key, target in imagevalues.items():
        if not 'difficulty' in target.label.keys() or target.label['difficulty'] == '':
            continue
        if 'nohasscoredata' in target.label.keys() and target.label['nohasscoredata']:
            continue

        evaluate_targets[key] = target

        musicname = target.label['musicname']
        if not musicname in evaluate_musictable.keys():
            evaluate_musictable[musicname] = {}
        
        playmode = target.label['playmode']
        if playmode is not None and not playmode in evaluate_musictable[musicname].keys():
            evaluate_musictable[musicname][playmode] = {}

        for difficulty in difficulties:
            level_key = f'level_{difficulty}'
            if not level_key in target.label.keys() or target.label[level_key] == '':
                continue
            if str.upper(difficulty) == target.label['difficulty']:
                targets['select'][difficulty][key] = target
            else:
                targets['noselect'][difficulty][key] = target
            
            level = target.label[level_key]
            evaluate_musictable[musicname][playmode][str.upper(difficulty)] = level

    for difficulty in difficulties:
        if 'nohasscoredata' in target.label.keys() and target.label['nohasscoredata']:
            continue

        define_target = musicselect_define['levels']['select'][difficulty]

        trim = (
            slice(define_target['trim'][0][0], define_target['trim'][0][1]),
            slice(define_target['trim'][1][0], define_target['trim'][1][1])
        )
        thresholds = define_target['thresholds']
        table = {}

        for key, target in targets['select'][difficulty].items():
            level_key = f'level_{difficulty}'
            value = target.label[level_key]
            trimmed = target.np_value[trim]
            filtereds = []
            for index in range(len(thresholds)):
                threshold = thresholds[index]
                masked = np.where((threshold[0]<=trimmed[:,:,index])&(trimmed[:,:,index]<=threshold[1]), 1, 0)
                filtereds.append(masked)
            bins = np.where((filtereds[0]==1)&(filtereds[1]==1)&(filtereds[2]==1), 1, 0)
            hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
            tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
            if tablekey in table.keys() and value != table[tablekey]:
                report.error(f'Duplicate select {difficulty} {tablekey} {value} {table[tablekey]}')
            table[tablekey] = value

        for level in define.value_list['levels']:
            keys = [k for k, v in table.items() if v == level]
            report.append_log(f'select {difficulty} {level}: {keys}')

        resource['levels']['select'][difficulty] = {
            'trim': trim,
            'thresholds': thresholds,
            'table': table
        }

    for difficulty in difficulties:
        define_target = musicselect_define['levels']['noselect'][difficulty]

        trim = (
            slice(define_target['trim'][0][0], define_target['trim'][0][1]),
            slice(define_target['trim'][1][0], define_target['trim'][1][1])
        )
        threshold = define_target['threshold']
        table = {}

        for key, target in targets['noselect'][difficulty].items():
            level_key = f'level_{difficulty}'
            value = target.label[level_key]
            trimmed = target.np_value[trim]
            filtereds = []
            for index in range(trimmed.shape[2]):
                masked = np.where((threshold[0]<=trimmed[:,:,index])&(trimmed[:,:,index]<=threshold[1]), 1, 0)
                filtereds.append(masked)
            bins = np.where((filtereds[0]==1)&(filtereds[1]==1)&(filtereds[2]==1), 1, 0)
            hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
            tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
            if tablekey in table.keys() and value != table[tablekey]:
                report.error(f'Duplicate noselect {difficulty} {tablekey} {value} {table[tablekey]}')
            table[tablekey] = value
        
        for level in define.value_list['levels']:
            keys = [k for k, v in table.items() if v == level]
            report.append_log(f'noselect {difficulty} {level}: {keys}')

        resource['levels']['noselect'][difficulty] = {
            'trim': trim,
            'threshold': threshold,
            'table': table
        }

    for key, target in evaluate_targets.items():
        selectdifficulty = None
        for selectstate in selectstatus:
            for difficulty in difficulties:
                level_key = f'level_{difficulty}'
                value = target.label[level_key]
                if selectstate == 'select':
                    trimmed = target.np_value[resource['levels'][selectstate][difficulty]['trim']]
                    filtereds = []
                    for index in range(len(resource['levels'][selectstate][difficulty]['thresholds'])):
                        threshold = resource['levels'][selectstate][difficulty]['thresholds'][index]
                        masked = np.where((threshold[0]<=trimmed[:,:,index])&(trimmed[:,:,index]<=threshold[1]), 1, 0)
                        filtereds.append(masked)
                    bins = np.where((filtereds[0]==1)&(filtereds[1]==1)&(filtereds[2]==1), 1, 0)
                    hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
                    tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
                if selectstate == 'noselect':
                    trimmed = target.np_value[resource['levels'][selectstate][difficulty]['trim']]
                    filtereds = []
                    for index in range(trimmed.shape[2]):
                        masked = np.where((threshold[0]<=trimmed[:,:,index])&(trimmed[:,:,index]<=threshold[1]), 1, 0)
                        filtereds.append(masked)
                    bins = np.where((filtereds[0]==1)&(filtereds[1]==1)&(filtereds[2]==1), 1, 0)
                    hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
                    tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])

                if tablekey in resource['levels'][selectstate][difficulty]['table'].keys():
                    levelresult = resource['levels'][selectstate][difficulty]['table'][tablekey]
                    if level_key in target.label.keys() and target.label[level_key] != "" and levelresult == target.label[level_key]:
                        report.through()
                    else:
                        report.saveimage_errorvalue(trimmed, f'{key}-{difficulty}-{target.label[level_key]}.png')
                        report.error(f'Mismatch {key} {difficulty} {levelresult} {target.label[level_key]}')

                    if selectstate == 'select' and selectdifficulty is None and str.upper(difficulty) == target.label['difficulty']:
                        selectdifficulty = difficulty

        if selectdifficulty is not None:
            if str.upper(selectdifficulty) == target.label['difficulty']:
                report.through()
            else:
                report.error(f'Mismatch {key} select {selectdifficulty} {target.label["difficulty"]}')
        else:
            report.error(f'Unrecognized {key} {target.label["difficulty"]}')

    report.report()

def larning_cleartype():
    report = Report('musicselect_cleartype')

    define_target = musicselect_define['cleartype']

    trim = (
        slice(define_target['trim'][0][0], define_target['trim'][0][1]),
        slice(define_target['trim'][1][0], define_target['trim'][1][1]),
        define_target['trim'][2]
    )

    table = {}
    evaluate_targets = {}
    for key, target in imagevalues.items():
        if 'cleartype' in target.label.keys() and target.label['cleartype'] != "":
            value = target.label['cleartype']
            trimmed = target.np_value[trim]
            uniques, counts = np.unique(trimmed, return_counts=True)
            color = uniques[np.argmax(counts)]
            table[color] = value

        evaluate_targets[key] = target
    
    for value in define.value_list['clear_types']:
        keys = [k for k, v in table.items() if v == value]
        if not len(keys):
            report.append_log(f'Not found key {value}')
        report.append_log(f'{value}: {keys}')

    for key, target in evaluate_targets.items():
        if 'cleartype' in target.label.keys() and target.label['cleartype'] != "":
            trimmed = target.np_value[trim]
            uniques, counts = np.unique(trimmed, return_counts=True)
            color = uniques[np.argmax(counts)]

            result = None
            if color in table.keys():
                result = table[color]
            
            if target.label['cleartype'] == result:
                report.through()
            else:
                report.saveimage_errorvalue(trimmed, f'{key}.png')
                report.error(f'Mismatch {result} {key}')

    resource['cleartype'] = {
        'trim': trim,
        'table': table
    }

    report.report()

def larning_djlevel():
    report = Report('musicselect_djlevel')

    define_target = musicselect_define['djlevel']

    trim = (
        slice(define_target['trim'][0][0], define_target['trim'][0][1]),
        slice(define_target['trim'][1][0], define_target['trim'][1][1]),
        define_target['trim'][2]
    )
    maskvalue = define_target['maskvalue']

    table = {}
    evaluate_targets = {}
    for key, target in imagevalues.items():
        if not 'djlevel' in target.label.keys() or target.label['djlevel'] == "":
            continue

        if 'djlevel' in target.label.keys() and target.label['djlevel'] != "":
            value = target.label['djlevel']
            trimmed = target.np_value[trim]
            count = np.count_nonzero(trimmed==maskvalue)
            table[count] = value

        evaluate_targets[key] = target
    
    for value in define.value_list['dj_levels']:
        keys = [k for k, v in table.items() if v == value]
        if not len(keys):
            report.append_log(f'Not found key {value}')
        report.append_log(f'{value}: {keys}')

    for key, target in evaluate_targets.items():
        if 'dj_level' in target.label.keys() and target.label['djlevel'] != "":
            trimmed = target.np_value[trim]
            count = np.count_nonzero(trimmed==maskvalue)

            result = None
            if count in table.keys():
                result = table[count]
            
            if target.label['djlevel'] == result:
                report.through()
            else:
                report.saveimage_errorvalue(trimmed, f'{key}.png')
                report.error(f'Mismatch {result} {key}({count})')

    resource['djlevel'] = {
        'trim': trim,
        'maskvalue': maskvalue,
        'table': table
    }

    report.report()

def larning_number():
    report = Report('musicselect_number')

    define_target_score = musicselect_define['score']
    define_target_misscount = musicselect_define['misscount']
    define_target_number = musicselect_define['number']

    trim_score = (
        slice(define_target_score['trim'][0][0], define_target_score['trim'][0][1]),
        slice(define_target_score['trim'][1][0], define_target_score['trim'][1][1]),
        define_target_score['trim'][2]
    )
    digit_score = define_target_score['digit']

    trim_misscount = (
        slice(define_target_misscount['trim'][0][0], define_target_misscount['trim'][0][1]),
        slice(define_target_misscount['trim'][1][0], define_target_misscount['trim'][1][1]),
        define_target_misscount['trim'][2]
    )
    digit_misscount = define_target_misscount['digit']

    trim_number = (
        slice(define_target_number['trim'][0][0], define_target_number['trim'][0][1], define_target_number['trim'][0][2]),
        slice(define_target_number['trim'][1][0], define_target_number['trim'][1][1], define_target_number['trim'][1][2])
    )
    maskvalue = define_target_number['maskvalue']

    table = {}
    evaluate_targets = {}
    targetkeys = {}
    for key, target in imagevalues.items():
        if 'score' in target.label.keys() and target.label['score'] != "":
            value = int(target.label['score']) % 10
            trimmed = target.np_value[trim_score]
            splitted = np.hsplit(trimmed, digit_score)
            trimmed_once = splitted[-1][trim_number]
            bins = np.where(trimmed_once==maskvalue, 1, 0).T
            hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
            tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
            if not tablekey in table or not value in table.values():
                table[tablekey] = value
                targetkeys[value] = key

            evaluate_targets[f'score_{key}'] = target

        if 'misscount' in target.label.keys() and target.label['misscount'] != "":
            value = int(target.label['misscount']) % 10
            trimmed = target.np_value[trim_misscount]
            splitted = np.hsplit(trimmed, digit_misscount)
            trimmed_once = splitted[-1][trim_number]
            bins = np.where(trimmed_once==maskvalue, 1, 0).T
            hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
            tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
            if not tablekey in table or not value in table.values():
                table[tablekey] = value
                targetkeys[value] = key
        
            evaluate_targets[f'miss_count_{key}'] = target
    
    for value in range(10):
        keys = [k for k, v in table.items() if v == value]
        if not len(keys):
            report.append_log(f'Not found key {value}')
        else:
            report.append_log(f'{value}: {keys} ({targetkeys[value]})')

    for key, target in evaluate_targets.items():
        if 'score' in target.label.keys() and target.label['score'] != "":
            trimmed = target.np_value[trim_score]

            result = 0
            keys = []
            for dig in range(digit_score):
                splitted = np.hsplit(trimmed, digit_score)
                trimmed_once = splitted[-(dig+1)][trim_number]
                bins = np.where(trimmed_once==maskvalue, 1, 0).T
                hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
                tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
                keys.append(tablekey)
                if not tablekey in table.keys():
                    break
                result += 10 ** dig * table[tablekey]
            
            if int(target.label['score']) == result:
                report.through()
            else:
                report.saveimage_errorvalue(trimmed, f'{key}.png')
                report.error(f"Mismatch score {result} {target.label['score']} {key}")

        if 'misscount' in target.label.keys() and target.label['misscount'] != "":
            trimmed = target.np_value[trim_misscount]

            result = 0
            for dig in range(digit_misscount):
                splitted = np.hsplit(trimmed, digit_misscount)
                trimmed_once = splitted[-(dig+1)][trim_number]
                bins = np.where(trimmed_once==maskvalue, 1, 0).T
                hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
                tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
                if not tablekey in table.keys():
                    break
                result += 10 ** dig * table[tablekey]
            
            if int(target.label['misscount']) == result:
                report.through()
            else:
                report.saveimage_errorvalue(trimmed, f'{key}.png')
                report.error(f"Mismatch miss count {result} {target.label['misscount']} {key}")

    resource['score'] = {
        'trim': trim_score,
        'digit': digit_score
    }
    resource['misscount'] = {
        'trim': trim_misscount,
        'digit': digit_misscount
    }
    resource['number'] = {
        'trim': trim_number,
        'maskvalue': maskvalue,
        'table': table
    }

    report.report()

def larning_musicname_convertdefine():
    resource_target = resource['musicname']

    define_target = musicselect_define['musicname']

    arcade = define_target['arcade']
    infinitas = define_target['infinitas']
    leggendaria = define_target['leggendaria']

    resource_target['arcade'] = {
        'trim': (
            slice(arcade['trim'][0][0], arcade['trim'][0][1]),
            slice(arcade['trim'][1][0], arcade['trim'][1][1])
        ),
        'thresholds': arcade['thresholds']
    }

    resource_target['infinitas'] = {
        'trim': (
            slice(infinitas['trim'][0][0], infinitas['trim'][0][1]),
            slice(infinitas['trim'][1][0], infinitas['trim'][1][1], infinitas['trim'][1][2])
        ),
        'thresholds': infinitas['thresholds']
    }

    resource_target['leggendaria'] = {
        'trim': (
            slice(leggendaria['trim'][0][0], leggendaria['trim'][0][1]),
            slice(leggendaria['trim'][1][0], leggendaria['trim'][1][1], leggendaria['trim'][1][2])
        ),
        'thresholds': leggendaria['thresholds']
    }

def larning_musicname_arcade(targets, report):
    resource_target = resource['musicname']['arcade']
    th = resource_target['thresholds']
    key_valid_count_minimum = musicselect_define['musicname']['arcade']['key_valid_count_minimum']

    table = resource_target['table'] = {}

    output = []

    evaluate = {}
    minimum_valid_count = (
        None,
        None,
        (resource_target['trim'][0].stop-resource_target['trim'][0].start) * (resource_target['trim'][1].stop-resource_target['trim'][1].start)
    )
    for key, target in targets.items():
        musicname = target.label['musicname']

        cropped = target.np_value[resource_target['trim']]
        masked = np.where((cropped[:,:,0]==cropped[:,:,1])&(cropped[:,:,0]==cropped[:,:,2]),cropped[:,:,0], 0)
        bins = [np.where((th[i][0]<=masked[i])&(masked[i]<=th[i][1]), 1, 0) for i in range(masked.shape[0])]
        shrunk = [line[::2]&line[1::2] for line in bins]
        valid_count = np.count_nonzero(shrunk)
        if valid_count < minimum_valid_count[2]:
            minimum_valid_count = (musicname, key, valid_count)
        hexes = [line[::4]*8+line[1::4]*4+line[2::4]*2+line[3::4] for line in shrunk]
        recogkeys = [''.join([format(v, '0x') for v in line]) for line in hexes]
        target = table
        for recogkey in recogkeys[:-1]:
            if not recogkey in target.keys():
                target[recogkey] = {}
            target = target[recogkey]
        if not recogkeys[-1] in target.keys():
            target[recogkeys[-1]] = musicname
            output.append(f'{key}: ({valid_count}) {musicname} {recogkeys}')
            if not musicname in evaluate.keys():
                evaluate[musicname] = []
            evaluate[musicname].append(''.join(recogkeys))
        else:
            if musicname != target[recogkeys[-1]]:
                report.error(f'{musicname}: arcade duplicate {target[recogkeys[-1]]}({key})')
                report.saveimage_errorvalue(cropped, f'duplicate-arcade-{key}')
        
        if not musicname in evaluate.keys():
            evaluate[musicname] = []
        evaluate[musicname].append(''.join(recogkeys))
    
    if minimum_valid_count[2] < key_valid_count_minimum:
        report.error(f'Arcade key valid count is less than {key_valid_count_minimum}: {minimum_valid_count[0]} {minimum_valid_count[1]} {minimum_valid_count[2]}')

    for musicname in evaluate.keys():
        count = len(set(evaluate[musicname]))
        if(count != 1):
            report.error(f'duplicate key arcade {musicname}: {count}')
    
    output_path = join(musicname_output_dirpath, 'arcade.txt')
    with open(output_path, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))

def larning_musicname_infinitas(targets, report):
    resource_target = resource['musicname']['infinitas']
    key_valid_count_minimum = musicselect_define['musicname']['infinitas']['key_valid_count_minimum']

    table = resource_target['table'] = {}

    output = []

    evaluate = {}
    minimum_valid_count = (
        None,
        None,
        (resource_target['trim'][0].stop-resource_target['trim'][0].start) * (resource_target['trim'][1].stop-resource_target['trim'][1].start)
    )
    for key, target in targets.items():
        musicname = target.label['musicname']

        cropped = target.np_value[resource_target['trim']]
        filtereds = []
        for index in range(len(resource_target['thresholds'])):
            threshold = resource_target['thresholds'][index]
            masked = np.where((threshold[0]<=cropped[:,:,index])&(cropped[:,:,index]<=threshold[1]), 1, 0)
            filtereds.append(masked)
        bins = np.where((filtereds[0]==1)&(filtereds[1]==1)&(filtereds[2]==1), 1, 0)
        valid_count = np.count_nonzero(bins)
        if valid_count < minimum_valid_count[2]:
            minimum_valid_count = (musicname, key, valid_count)
        hexes = [line[::4]*8+line[1::4]*4+line[2::4]*2+line[3::4] for line in bins]
        recogkeys = [''.join([format(v, '0x') for v in line]) for line in hexes]
        target = table
        for recogkey in recogkeys[:-1]:
            if not recogkey in target.keys():
                target[recogkey] = {}
            target = target[recogkey]
        if not recogkeys[-1] in target.keys():
            target[recogkeys[-1]] = musicname
            output.append(f'{key}: ({valid_count}) {musicname} {recogkeys}')
            if not musicname in evaluate.keys():
                evaluate[musicname] = []
            evaluate[musicname].append(''.join(recogkeys))
        else:
            if musicname != target[recogkeys[-1]]:
                report.error(f'{musicname}: infinitas duplicate {target[recogkeys[-1]]}({key})')
                report.saveimage_errorvalue(cropped, f'duplicate-infinitas-{key}')
    
    if minimum_valid_count[2] < key_valid_count_minimum:
        report.error(f'Infinitas key valid count is less than {key_valid_count_minimum}: {minimum_valid_count[0]} {minimum_valid_count[1]} {minimum_valid_count[2]}')

    for musicname in evaluate.keys():
        count = len(set(evaluate[musicname]))
        if(count != 1):
            report.error(f'duplicate key infinitas {musicname}: {count}')
    
    output_path = join(musicname_output_dirpath, 'infinitas.txt')
    with open(output_path, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))

def larning_musicname_leggendaria(targets, report):
    resource_target = resource['musicname']['leggendaria']
    key_valid_count_minimum = musicselect_define['musicname']['leggendaria']['key_valid_count_minimum']

    table = resource_target['table'] = {}

    output = []

    evaluate = {}
    minimum_valid_count = (
        None,
        None,
        (resource_target['trim'][0].stop-resource_target['trim'][0].start) * (resource_target['trim'][1].stop-resource_target['trim'][1].start)
    )
    for key, target in targets.items():
        musicname = target.label['musicname']

        cropped = target.np_value[resource_target['trim']]
        filtereds = []
        for index in range(len(resource_target['thresholds'])):
            threshold = resource_target['thresholds'][index]
            masked = np.where((threshold[0]<=cropped[:,:,index])&(cropped[:,:,index]<=threshold[1]), 1, 0)
            filtereds.append(masked)
        bins = np.where((filtereds[0]==1)&(filtereds[1]==1)&(filtereds[2]==1), 1, 0)
        valid_count = np.count_nonzero(bins)
        if valid_count < minimum_valid_count[2]:
            minimum_valid_count = (musicname, key, valid_count)
        hexes = [line[::4]*8+line[1::4]*4+line[2::4]*2+line[3::4] for line in bins]
        recogkeys = [''.join([format(v, '0x') for v in line]) for line in hexes]
        target = table
        for recogkey in recogkeys[:-1]:
            if not recogkey in target.keys():
                target[recogkey] = {}
            target = target[recogkey]
        if not recogkeys[-1] in target.keys():
            target[recogkeys[-1]] = musicname
            output.append(f'{key}: ({valid_count}) {musicname} {recogkeys}')
            if not musicname in evaluate.keys():
                evaluate[musicname] = []
            evaluate[musicname].append(''.join(recogkeys))
        else:
            if musicname != target[recogkeys[-1]]:
                report.error(f'{musicname}: leggendaria duplicate {target[recogkeys[-1]]}({key})')
                report.saveimage_errorvalue(cropped, f'duplicate-leggendaria-{key}')
        
        if not musicname in evaluate.keys():
            evaluate[musicname] = []
        evaluate[musicname].append(''.join(recogkeys))
    
    if minimum_valid_count[2] < key_valid_count_minimum:
        report.error(f'Leggendaria key valid count is less than {key_valid_count_minimum}: {minimum_valid_count[0]} {minimum_valid_count[1]} {minimum_valid_count[2]}')

    for musicname in evaluate.keys():
        count = len(set(evaluate[musicname]))
        if(count != 1):
            report.error(f'duplicate key leggendaria {musicname}: {count}')
    
    output_path = join(musicname_output_dirpath, 'leggendaria.txt')
    with open(output_path, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(output))

def larning_musicname():
    report = Report('musicselect_musicname')

    resource['musicname'] = {}

    larning_musicname_convertdefine()
    
    targets = {}
    evaluate_targets = {}
    for musictype in ['ARCADE', 'INFINITAS', 'LEGGENDARIA']:
        targets[musictype] = {}

    for key, target in imagevalues.items():
        if not 'musictype' in target.label.keys() or target.label['musictype'] == "":
            continue
        if not 'musicname' in target.label.keys() or target.label['musicname'] == "":
            continue

        targets[target.label['musictype']][key] = target
        evaluate_targets[key] = target

    larning_musicname_arcade(targets['ARCADE'], report)
    larning_musicname_infinitas(targets['INFINITAS'], report)
    larning_musicname_leggendaria(targets['LEGGENDARIA'], report)
    
    for key, target in evaluate_targets.items():
        musicname = target.label['musicname']

        resultmusicname = None

        if resultmusicname is None:
            resource_target = resource['musicname']['infinitas']
            cropped = target.np_value[resource_target['trim']]
            filtereds = []
            for index in range(len(resource_target['thresholds'])):
                threshold = resource_target['thresholds'][index]
                masked = np.where((threshold[0]<=cropped[:,:,index])&(cropped[:,:,index]<=threshold[1]), 1, 0)
                filtereds.append(masked)
            bins = np.where((filtereds[0]==1)&(filtereds[1]==1)&(filtereds[2]==1), 1, 0)
            hexes = [line[::4]*8+line[1::4]*4+line[2::4]*2+line[3::4] for line in bins]
            recogkeys = [''.join([format(v, '0x') for v in line]) for line in hexes]
            tabletarget = resource_target['table']
            for recogkey in recogkeys:
                if not recogkey in tabletarget.keys():
                    break
                if type(tabletarget[recogkey]) is str:
                    resultmusicname = tabletarget[recogkey]
                    break
                tabletarget = tabletarget[recogkey]
        
        if resultmusicname is None:
            resource_target = resource['musicname']['leggendaria']
            cropped = target.np_value[resource_target['trim']]
            filtereds = []
            for index in range(len(resource_target['thresholds'])):
                threshold = resource_target['thresholds'][index]
                masked = np.where((threshold[0]<=cropped[:,:,index])&(cropped[:,:,index]<=threshold[1]), 1, 0)
                filtereds.append(masked)
            bins = np.where((filtereds[0]==1)&(filtereds[1]==1)&(filtereds[2]==1), 1, 0)
            hexes = [line[::4]*8+line[1::4]*4+line[2::4]*2+line[3::4] for line in bins]
            recogkeys = [''.join([format(v, '0x') for v in line]) for line in hexes]
            tabletarget = resource_target['table']
            for recogkey in recogkeys:
                if not recogkey in tabletarget.keys():
                    break
                if type(tabletarget[recogkey]) is str:
                    resultmusicname = tabletarget[recogkey]
                    break
                tabletarget = tabletarget[recogkey]

        if resultmusicname is None:
            resource_target = resource['musicname']['arcade']
            thresholds = resource_target['thresholds']
            cropped = target.np_value[resource_target['trim']]
            masked = np.where((cropped[:,:,0]==cropped[:,:,1])&(cropped[:,:,0]==cropped[:,:,2]),cropped[:,:,0], 0)
            bins = [np.where((thresholds[i][0]<=masked[i])&(masked[i]<=thresholds[i][1]), 1, 0) for i in range(masked.shape[0])]
            shrunk = [line[::2]&line[1::2] for line in bins]
            hexes = [line[::4]*8+line[1::4]*4+line[2::4]*2+line[3::4] for line in shrunk]
            recogkeys = [''.join([format(v, '0x') for v in line]) for line in hexes]
            tabletarget = resource_target['table']
            for recogkey in recogkeys:
                if not recogkey in tabletarget.keys():
                    break
                if type(tabletarget[recogkey]) is str:
                    resultmusicname = tabletarget[recogkey]
                    break
                tabletarget = tabletarget[recogkey]
    
        if(musicname == resultmusicname):
            report.through()
        else:
            report.error(f'{key}: wrong recognition {musicname} {resultmusicname}')
            report.saveimage_errorvalue(cropped, f'maskerror-{key}')

    report.report()

def larning_version():
    report = Report('musicselect_version')

    define_target = musicselect_define['version']

    versions = [
        '1st',
        'substream',
        '2nd style',
        '3rd style',
        '4th style',
        '5th style',
        '6th style',
        '7th style',
        '8th style',
        '9th style',
        '10th style',
        'IIDX RED',
        'HAPPY SKY',
        'DistorteD',
        'GOLD',
        'DJ TROOPERS',
        'EMPRESS',
        'SIRIUS',
        'Resort Anthem',
        'Lincle',
        'tricoro',
        'SPADA',
        'PENDUAL',
        'copula',
        'SINOBUZ',
        'CANNON BALLERS',
        'Rootage',
        'HEROIC VERSE',
        'BISTROVER',
        'CastHour',
        'RESIDENT',
        'EPOLIS',
        'INFINITAS',
    ]

    tables = []
    for part in define_target:
        tables.append({
            'trim': (
                slice(part['trim'][0][0], part['trim'][0][1]),
                slice(part['trim'][1][0], part['trim'][1][1])
            ),
            'keys': {}
        })

    masktargets = {}
    for key, target in imagevalues.items():
        if not 'version' in target.label.keys() or not target.label['version'] in versions:
            continue
        
        version = target.label['version']
        if not version in masktargets.keys():
            masktargets[version] = []
        masktargets[version].append(target.np_value)
    
    evaluate_targets = {}
    keys = {}
    for version in versions:
        keys[version] = []
    for key, target in imagevalues.items():
        if not 'version' in target.label.keys() or not target.label['version'] in versions:
            continue
        
        value = target.label['version']

        for table in tables:
            trim = table['trim']
            cropped = target.np_value[trim]
            reshaped = cropped.reshape(cropped.shape[0]*cropped.shape[1], cropped.shape[2])
            hexes = [''.join([format(b, '02x') for b in point]) for point in reshaped]
            tablekey = ''.join(hexes)

            if not value in table['keys']:
                table['keys'][value] = []
            table['keys'][value].append(tablekey)

        evaluate_targets[key] = target

        if 'musicname' in target.label.keys() and 'version' in target.label.keys():
            musicname = target.label['musicname']
            version = target.label['version']
            if musicname is not None and not musicname in evaluate_musictable.keys():
                evaluate_musictable[musicname] = {}
            evaluate_musictable[musicname]['version'] = version
    
    for table in tables:
        table['table'] = {}
        for version in table['keys'].keys():
            setted = set(table['keys'][version])
            if(len(setted) == 1):
                table['table'][[*setted][0]] = version
        del table['keys']

    for key, target in evaluate_targets.items():
        value = target.label['version']
        result = None
        for table in tables:
            cropped = target.np_value[table['trim']]
            reshaped = cropped.reshape(cropped.shape[0]*cropped.shape[1], cropped.shape[2])
            hexes = [''.join([format(b, '02x') for b in point]) for point in reshaped]
            tablekey = ''.join(hexes)

            if tablekey in table['table'].keys():
                result = table['table'][tablekey]
                break
        
        if result == target.label['version']:
            report.through()
        else:
            report.saveimage_errorvalue(cropped, key)
            report.error(f'Mismatch {result} {key}')

    for version in versions:
        is_ok = False
        for table in tables:
            target = table['table']
            if version in target.values():
                is_ok = True
                report.append_log(f'{version} key: {[k for k, v in target.items() if v == version][0]}')
                break
        if not is_ok:
            report.error(f'Undefined {version}')

    resource['version'] = tables

    report.report()

def evaluate():
    report = Report('musicselect_evaluate')

    table = musictable['musics']
    for musicname in table.keys():
        escaped = musicname.encode('unicode-escape').decode('utf-8')
        if musicname in evaluate_musictable.keys():
            if not 'version' in evaluate_musictable[musicname].keys():
                report.error(f'Not registered version {musicname}')
            
            for playmode in define.value_list['play_modes']:
                if playmode in evaluate_musictable[musicname].keys():
                    for difficulty in define.value_list['difficulties']:
                        resultlevel = None
                        tablelevel = None

                        if difficulty in evaluate_musictable[musicname][playmode].keys():
                            resultlevel = evaluate_musictable[musicname][playmode][difficulty]
                        if difficulty in table[musicname][playmode].keys():
                            tablelevel = table[musicname][playmode][difficulty]

                        if resultlevel != tablelevel:
                            report.error(f'Mismatch {musicname} {playmode} {difficulty}: {resultlevel} {tablelevel}({escaped})')
                else:
                    report.error(f'Not registered {musicname} {playmode}({escaped})')
        else:
            report.error(f'Not registered {musicname}({escaped})')
    
    for musicname in evaluate_musictable.keys():
        if musicname != "" and not musicname in table.keys():
            report.error(f'Not exist {musicname}')
    
    report.report()

if __name__ == '__main__':
    try:
        with open(label_filepath) as f:
            labels = json.load(f)
    except Exception:
        print(f"{label_filepath}を読み込めませんでした。")
        exit()

    musicselect_define = load_define()
    if musicselect_define is None:
        exit()

    musictable = load_resource_serialized(f'musictable{define.musictable_version}')

    imagevalues = load_images(labels)
    
    resource = {}
    evaluate_musictable = {}

    larning_playmode()
    larning_levels()
    larning_cleartype()
    larning_djlevel()
    larning_number()
    larning_version()
    larning_musicname()

    evaluate()

    filename = f'musicselect{define.musicselect_recognition_version}.res'
    save_resource_serialized(filename, resource)
