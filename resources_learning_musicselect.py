import json
from sys import exit
from os.path import join,isfile
from logging import getLogger

logger = getLogger(__name__)
logger.debug(f'loaded {__name__}')

from PIL import Image
import numpy as np

from define import Playmodes,define
from data_collection import label_musicselect_filepath,images_musicselect_basepath
from resources import load_resource_serialized
from resources_generate import Report,save_resource_serialized,registries_dirname
from resources_learning import learning_multivaluemask,learning

recognition_define_filename = 'define_recognition_musicselect.json'
recognition_define_filepath = join(registries_dirname, recognition_define_filename)

versions_filepath = join(registries_dirname, 'versions.txt')

class ImageValues():
    def __init__(self, np_value, label):
        self.np_value = np_value
        self.label = label

def load_images(labels:dict) -> dict:
    keys = [key for key in labels.keys()]

    imagevaleus = {}
    for filename in keys:
        if 'ignore' in labels[filename].keys() and labels[filename]['ignore']:
            continue

        filepath = join(images_musicselect_basepath, filename)
        if not isfile(filepath):
            continue

        np_value = np.array(Image.open(filepath), dtype=np.uint8)
        imagevaleus[filename] = ImageValues(np_value, labels[filename])
    
    return imagevaleus

def load_define() -> dict:
    try:
        with open(recognition_define_filepath) as f:
            ret = json.load(f)
    except Exception:
        print(f"{recognition_define_filepath}を読み込めませんでした。")
        return None
    
    return ret

def learning_playmode():
    report_playmode = Report('musicselect_playmode')

    define_target = musicselect_define['playmode']

    trim = (
        slice(define_target['trim'][0][0], define_target['trim'][0][1]),
        slice(define_target['trim'][1][0], define_target['trim'][1][1]),
        define_target['trim'][2]
    )
    maskvalue = define_target['maskvalue']

    learning_targets = {}
    evaluate_targets = {}
    for key, target in imagevalues.items():
        if not 'playmode' in target.label.keys() or target.label['playmode'] == '':
            continue
        
        value = target.label['playmode']
        trimmed = target.np_value[trim]
        if not value in learning_targets.keys():
            learning_targets[value] = {}
        learning_targets[value][key] = trimmed

        evaluate_targets[key] = target
    
    report_playmode.append_log(f'Source count: {len(learning_targets)}')

    table = learning_multivaluemask(learning_targets, report_playmode, maskvalue)
    if table is None:
        report_playmode.report_playmode()
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
            report_playmode.through()
        else:
            report_playmode.saveimage_errorvalue(trimmed, key)
            report_playmode.error(f'Mismatch {result} {key}')

    resource['playmode'] = {
        'trim': trim,
        'maskvalue': maskvalue,
        'table': table
    }

    report_playmode.report()

    if not report_playmode.count_error:
        report.through()
    else:
        report.error('Error playmode')

def learning_levels():
    report_levels = Report(f'musicselect_levels')

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
        if not 'after260312' in target.label.keys() or not target.label['after260312']:
            continue

        evaluate_targets[key] = target

        songname = target.label['musicname']
        if not songname in evaluate_musictable.keys():
            evaluate_musictable[songname] = {}
        
        playmode = target.label['playmode']
        if playmode is not None and not playmode in evaluate_musictable[songname].keys():
            evaluate_musictable[songname][playmode] = {}

        for difficulty in difficulties:
            level_key = f'level_{difficulty}'
            if not level_key in target.label.keys() or target.label[level_key] == '':
                continue
            if str.upper(difficulty) == target.label['difficulty']:
                targets['select'][difficulty][key] = target
            else:
                targets['noselect'][difficulty][key] = target
            
            level = target.label[level_key]
            evaluate_musictable[songname][playmode][str.upper(difficulty)] = level

    for difficulty in difficulties:
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
                report_levels.error(f'Duplicate select {difficulty} {tablekey} {value} {table[tablekey]}')
            table[tablekey] = value

        for level in define.value_list['levels']:
            keys = [k for k, v in table.items() if v == level]
            report_levels.append_log(f'select {difficulty} {level}: {keys}')

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
                report_levels.error(f'Duplicate noselect {difficulty} {tablekey} {value} {table[tablekey]}')
            table[tablekey] = value
        
        for level in define.value_list['levels']:
            keys = [k for k, v in table.items() if v == level]
            report_levels.append_log(f'noselect {difficulty} {level}: {keys}')

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
                        report_levels.through()
                    else:
                        report_levels.saveimage_errorvalue(trimmed, f'{key}-{difficulty}-{target.label[level_key]}.png')
                        report_levels.error(f'Mismatch {key} {difficulty} {levelresult} {target.label[level_key]}')

                    if selectstate == 'select' and selectdifficulty is None and str.upper(difficulty) == target.label['difficulty']:
                        selectdifficulty = difficulty

        if selectdifficulty is not None:
            if str.upper(selectdifficulty) == target.label['difficulty']:
                report_levels.through()
            else:
                report_levels.error(f'Mismatch {key} select {selectdifficulty} {target.label["difficulty"]}')
        else:
            report_levels.error(f'Unrecognized {key} {target.label["difficulty"]}')

    report_levels.report()
    
    if not report_levels.count_error:
        report.through()
    else:
        report.error('Error levels')

def learning_hasscoredata():
    report_hasscoredata = Report('musicselect_hasscoredata')

    define_target = musicselect_define['hasscoredata']

    trim = (
        slice(define_target['trim'][0][0], define_target['trim'][0][1]),
        slice(define_target['trim'][1][0], define_target['trim'][1][1]),
        define_target['trim'][2]
    )

    learning_targets = {}
    evaluate_targets = {}
    for key, target in imagevalues.items():
        if not 'nohasscoredata' in target.label.keys():
            continue

        trimmed = target.np_value[trim]

        if not target.label['nohasscoredata']:
            learning_targets[key] = trimmed

        evaluate_targets[key] = {'value': not target.label['nohasscoredata'], 'trimmed': trimmed}
    
    report_hasscoredata.append_log(f'source count: {len(learning_targets)}')

    result = learning(learning_targets, report_hasscoredata)
    if result is None:
        report_hasscoredata.report_hasscoredata()
        return
    
    for key, target in evaluate_targets.items():
        is_hasscoredata = target['value']
        recoged = np.all((result==0)|(target['trimmed']==result))
        if (recoged and is_hasscoredata) or (not recoged and not is_hasscoredata):
            report_hasscoredata.through()
        else:
            report_hasscoredata.error(f'Mismatch {is_hasscoredata} {key}')

    resource['hasscoredata'] = {
        'trim': trim,
        'mask': result
    }

    report_hasscoredata.report()
    
    if not report_hasscoredata.count_error:
        report.through()
    else:
        report.error('Error hasscoredata')

def learning_cleartype():
    report_cleartype = Report('musicselect_cleartype')

    define_target = musicselect_define['cleartype']

    trim = (
        slice(define_target['trim'][0][0], define_target['trim'][0][1]),
        slice(define_target['trim'][1][0], define_target['trim'][1][1]),
        define_target['trim'][2]
    )

    table = {}
    evaluate_targets = {}
    for key, target in imagevalues.items():
        if not 'cleartype' in target.label.keys() or target.label['cleartype'] == "":
            continue

        value = target.label['cleartype']
        trimmed = target.np_value[trim]
        uniques, counts = np.unique(trimmed, return_counts=True)
        color = uniques[np.argmax(counts)]
        table[color] = value

        evaluate_targets[key] = target
    
    for value in define.value_list['clear_types']:
        keys = [k for k, v in table.items() if v == value]
        if not len(keys):
            report_cleartype.append_log(f'Not found key {value}')
        report_cleartype.append_log(f'{value}: {keys}')

    for key, target in evaluate_targets.items():
        trimmed = target.np_value[trim]
        uniques, counts = np.unique(trimmed, return_counts=True)
        color = uniques[np.argmax(counts)]

        result = None
        if color in table.keys():
            result = table[color]
        
        if target.label['cleartype'] == result:
            report_cleartype.through()
        else:
            report_cleartype.saveimage_errorvalue(trimmed, f'{key}.png')
            report_cleartype.error(f'Mismatch {result} {key}')

    resource['cleartype'] = {
        'trim': trim,
        'table': table
    }

    report_cleartype.report()
    
    if not report_cleartype.count_error:
        report.through()
    else:
        report.error('Error cleartype')

def learning_djlevel():
    report_djlevel = Report('musicselect_djlevel')

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

        value = target.label['djlevel']
        trimmed = target.np_value[trim]
        count = np.count_nonzero(trimmed==maskvalue)
        table[count] = value

        evaluate_targets[key] = target
    
    for value in define.value_list['dj_levels']:
        keys = [k for k, v in table.items() if v == value]
        if not len(keys):
            report_djlevel.append_log(f'Not found key {value}')
        report_djlevel.append_log(f'{value}: {keys}')

    for key, target in evaluate_targets.items():
        trimmed = target.np_value[trim]
        count = np.count_nonzero(trimmed==maskvalue)

        result = None
        if count in table.keys():
            result = table[count]
        
        if target.label['djlevel'] == result:
            report_djlevel.through()
        else:
            report_djlevel.saveimage_errorvalue(trimmed, f'{key}.png')
            report_djlevel.error(f'Mismatch {result} {key}({count})')

    resource['djlevel'] = {
        'trim': trim,
        'maskvalue': maskvalue,
        'table': table
    }

    report_djlevel.report()
    
    if not report_djlevel.count_error:
        report.through()
    else:
        report.error('Error djlevel')

def learning_number():
    report_number = Report('musicselect_number')

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
            report_number.append_log(f'Not found key {value}')
        else:
            report_number.append_log(f'{value}: {keys} ({targetkeys[value]})')

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
                report_number.through()
            else:
                report_number.saveimage_errorvalue(trimmed, f'{key}.png')
                report_number.error(f"Mismatch score {result} {target.label['score']} {key}")

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
                report_number.through()
            else:
                report_number.saveimage_errorvalue(trimmed, f'{key}.png')
                report_number.error(f"Mismatch miss count {result} {target.label['misscount']} {key}")

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

    report_number.report()
    
    if not report_number.count_error:
        report.through()
    else:
        report.error('Error number')

def learning_songname_convertdefine():
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

def learning_songname_arcade(targets:dict, report:Report):
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
        songname = target.label['musicname']

        cropped = target.np_value[resource_target['trim']]
        masked = np.where((cropped[:,:,0]==cropped[:,:,1])&(cropped[:,:,0]==cropped[:,:,2]),cropped[:,:,0], 0)
        bins = [np.where((th[i][0]<=masked[i])&(masked[i]<=th[i][1]), 1, 0) for i in range(masked.shape[0])]
        shrunk = [line[::2]&line[1::2] for line in bins]
        valid_count = np.count_nonzero(shrunk)
        if valid_count < minimum_valid_count[2]:
            minimum_valid_count = (songname, key, valid_count)
        hexes = [line[::4]*8+line[1::4]*4+line[2::4]*2+line[3::4] for line in shrunk]
        recogkeys = [''.join([format(v, '0x') for v in line]) for line in hexes]
        target = table
        for recogkey in recogkeys[:-1]:
            if not recogkey in target.keys():
                target[recogkey] = {}
            target = target[recogkey]
        if not recogkeys[-1] in target.keys():
            target[recogkeys[-1]] = songname
            output.append(f'{key}: ({valid_count}) {songname} {recogkeys}')
            if not songname in evaluate.keys():
                evaluate[songname] = []
            evaluate[songname].append(''.join(recogkeys))
        else:
            if songname != target[recogkeys[-1]]:
                report.error(f'{songname}: arcade duplicate {target[recogkeys[-1]]}({key})')
                report.saveimage_errorvalue(cropped, f'duplicate-arcade-{key}')
        
        if not songname in evaluate.keys():
            evaluate[songname] = []
        evaluate[songname].append(''.join(recogkeys))
    
    if minimum_valid_count[2] < key_valid_count_minimum:
        report.error(f'Arcade key valid count is less than {key_valid_count_minimum}: {minimum_valid_count[0]} {minimum_valid_count[1]} {minimum_valid_count[2]}')

    for songname in evaluate.keys():
        count = len(set(evaluate[songname]))
        if(count != 1):
            report.error(f'duplicate key arcade {songname}: {count}')
    
    report.output_list(output, 'arcade.txt')

def learning_songname_infinitas(targets:dict, report:Report):
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
        songname = target.label['musicname']

        cropped = target.np_value[resource_target['trim']]
        filtereds = []
        for index in range(len(resource_target['thresholds'])):
            threshold = resource_target['thresholds'][index]
            masked = np.where((threshold[0]<=cropped[:,:,index])&(cropped[:,:,index]<=threshold[1]), 1, 0)
            filtereds.append(masked)
        bins = np.where((filtereds[0]==1)&(filtereds[1]==1)&(filtereds[2]==1), 1, 0)
        valid_count = np.count_nonzero(bins)
        if valid_count < minimum_valid_count[2]:
            minimum_valid_count = (songname, key, valid_count)
        hexes = [line[::4]*8+line[1::4]*4+line[2::4]*2+line[3::4] for line in bins]
        recogkeys = [''.join([format(v, '0x') for v in line]) for line in hexes]
        target = table
        for recogkey in recogkeys[:-1]:
            if not recogkey in target.keys():
                target[recogkey] = {}
            target = target[recogkey]
        if not recogkeys[-1] in target.keys():
            target[recogkeys[-1]] = songname
            output.append(f'{key}: ({valid_count}) {songname} {recogkeys}')
            if not songname in evaluate.keys():
                evaluate[songname] = []
            evaluate[songname].append(''.join(recogkeys))
        else:
            if songname != target[recogkeys[-1]]:
                report.error(f'{songname}: infinitas duplicate {target[recogkeys[-1]]}({key})')
                report.saveimage_errorvalue(cropped, f'duplicate-infinitas-{key}')
    
    if minimum_valid_count[2] < key_valid_count_minimum:
        report.error(f'Infinitas key valid count is less than {key_valid_count_minimum}: {minimum_valid_count[0]} {minimum_valid_count[1]} {minimum_valid_count[2]}')

    for songname in evaluate.keys():
        count = len(set(evaluate[songname]))
        if(count != 1):
            report.error(f'duplicate key infinitas {songname}: {count}')
    
    report.output_list(output, 'infinitas.txt')

def learning_songname_leggendaria(targets:dict, report:Report):
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
        songname = target.label['musicname']

        cropped = target.np_value[resource_target['trim']]
        filtereds = []
        for index in range(len(resource_target['thresholds'])):
            threshold = resource_target['thresholds'][index]
            masked = np.where((threshold[0]<=cropped[:,:,index])&(cropped[:,:,index]<=threshold[1]), 1, 0)
            filtereds.append(masked)
        bins = np.where((filtereds[0]==1)&(filtereds[1]==1)&(filtereds[2]==1), 1, 0)
        valid_count = np.count_nonzero(bins)
        if valid_count < minimum_valid_count[2]:
            minimum_valid_count = (songname, key, valid_count)
        hexes = [line[::4]*8+line[1::4]*4+line[2::4]*2+line[3::4] for line in bins]
        recogkeys = [''.join([format(v, '0x') for v in line]) for line in hexes]
        target = table
        for recogkey in recogkeys[:-1]:
            if not recogkey in target.keys():
                target[recogkey] = {}
            target = target[recogkey]
        if not recogkeys[-1] in target.keys():
            target[recogkeys[-1]] = songname
            output.append(f'{key}: ({valid_count}) {songname} {recogkeys}')
            if not songname in evaluate.keys():
                evaluate[songname] = []
            evaluate[songname].append(''.join(recogkeys))
        else:
            if songname != target[recogkeys[-1]]:
                report.error(f'{songname}: leggendaria duplicate {target[recogkeys[-1]]}({key})')
                report.saveimage_errorvalue(cropped, f'duplicate-leggendaria-{key}')
        
        if not songname in evaluate.keys():
            evaluate[songname] = []
        evaluate[songname].append(''.join(recogkeys))
    
    if minimum_valid_count[2] < key_valid_count_minimum:
        report.error(f'Leggendaria key valid count is less than {key_valid_count_minimum}: {minimum_valid_count[0]} {minimum_valid_count[1]} {minimum_valid_count[2]}')

    for songname in evaluate.keys():
        count = len(set(evaluate[songname]))
        if(count != 1):
            report.error(f'duplicate key leggendaria {songname}: {count}')
    
    report.output_list(output, 'leggendaria.txt')

def learning_songname():
    report_songname = Report('musicselect_musicname')

    resource['musicname'] = {}

    learning_songname_convertdefine()
    
    targets = {}
    evaluate_targets = {}
    for musictype in ['ARCADE', 'INFINITAS', 'LEGGENDARIA']:
        targets[musictype] = {}

    for key, target in imagevalues.items():
        if not 'musictype' in target.label.keys() or target.label['musictype'] == "":
            continue
        if not 'musicname' in target.label.keys() or target.label['musicname'] == "":
            continue
        if not 'after260312' in target.label.keys() or not target.label['after260312']:
            continue

        targets[target.label['musictype']][key] = target
        evaluate_targets[key] = target

    learning_songname_arcade(targets['ARCADE'], report_songname)
    learning_songname_infinitas(targets['INFINITAS'], report_songname)
    learning_songname_leggendaria(targets['LEGGENDARIA'], report_songname)
    
    for key, target in evaluate_targets.items():
        songname = target.label['musicname']

        resultsongname = None

        if resultsongname is None:
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
                    resultsongname = tabletarget[recogkey]
                    break
                tabletarget = tabletarget[recogkey]
        
        if resultsongname is None:
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
                    resultsongname = tabletarget[recogkey]
                    break
                tabletarget = tabletarget[recogkey]

        if resultsongname is None:
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
                    resultsongname = tabletarget[recogkey]
                    break
                tabletarget = tabletarget[recogkey]
    
        if(songname == resultsongname):
            report_songname.through()
        else:
            report_songname.error(f'{key}: wrong recognition {songname} {resultsongname}')
            report_songname.saveimage_errorvalue(cropped, f'maskerror-{key}')

    report_songname.report()
    
    if not report_songname.count_error:
        report.through()
    else:
        report.error('Error songname')

def learning_version():
    report_version = Report('musicselect_version')

    define_target = musicselect_define['version']

    versions = []
    try:
        with open(versions_filepath, 'r', encoding='utf-8') as f:
            for line in f.read().splitlines():
                versions.extend(line.strip().split('&'))
    except Exception:
        print(f"{versions_filepath}を読み込めませんでした。")
        return
    
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
        if not 'after260312' in target.label.keys() or not target.label['after260312']:
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
        if not 'after260312' in target.label.keys() or not target.label['after260312']:
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
            songname = target.label['musicname']
            version = target.label['version']
            if songname is not None and not songname in evaluate_musictable.keys():
                evaluate_musictable[songname] = {}
            evaluate_musictable[songname]['version'] = version
    
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
            report_version.through()
        else:
            report_version.saveimage_errorvalue(cropped, key)
            report_version.error(f'Mismatch {result} {key}')

    for version in versions:
        is_ok = False
        for table in tables:
            target = table['table']
            if version in target.values():
                is_ok = True
                report_version.append_log(f'{version} key: {[k for k, v in target.items() if v == version][0]}')
                break
        if not is_ok:
            report_version.error(f'Undefined {version}')

    resource['version'] = tables

    report_version.report()
    
    if not report_version.count_error:
        report.through()
    else:
        report.error('Error version')

def evaluate():
    report_evaluate = Report('musicselect_evaluate')

    table = musictable['musics']
    for songname in table.keys():
        escaped = songname.encode('unicode-escape').decode('utf-8')

        if songname in evaluate_musictable.keys():
            if not 'version' in evaluate_musictable[songname].keys():
                report_evaluate.error(f'Not registered version {songname}')
            else:
                resultversion = evaluate_musictable[songname]['version']
                tableversion = table[songname]['version']
                if resultversion != tableversion:
                    report_evaluate.error(f'Mismatch {songname} {resultversion} {tableversion}({escaped})')
            
            for playmode in Playmodes.values:
                if playmode in evaluate_musictable[songname].keys():
                    for difficulty in define.value_list['difficulties']:
                        resultlevel = None
                        tablelevel = None

                        if difficulty in evaluate_musictable[songname][playmode].keys():
                            resultlevel = evaluate_musictable[songname][playmode][difficulty]
                        if difficulty in table[songname][playmode].keys():
                            tablelevel = table[songname][playmode][difficulty]

                        if resultlevel != tablelevel:
                            report_evaluate.error(f'Mismatch {songname} {playmode} {difficulty}: {resultlevel} {tablelevel}({escaped})')
                # else:
                #     report_evaluate.error(f'Not registered {songname} {playmode}({escaped})')
        else:
            report_evaluate.error(f'Not registered {songname}({escaped})')
    
    for songname in evaluate_musictable.keys():
        if songname != "" and not songname in table.keys():
            report_evaluate.error(f'Not exist {songname}')
    
    report_evaluate.report()
    
    if not report_evaluate.count_error:
        report.through()
    else:
        report.error('Error evaluate')

if __name__ == '__main__':
    try:
        with open(label_musicselect_filepath) as f:
            labels = json.load(f)
    except Exception:
        print(f"{label_musicselect_filepath}を読み込めませんでした。")
        exit()

    musicselect_define = load_define()
    if musicselect_define is None:
        exit()

    musictable = load_resource_serialized(f'musictable{define.musictable_version}', True)

    imagevalues = load_images(labels)
    
    resource = {}
    evaluate_musictable = {}

    report = Report('musicselect')

    learning_playmode()
    learning_levels()
    learning_hasscoredata()
    learning_cleartype()
    learning_djlevel()
    learning_number()
    learning_version()
    learning_songname()

    evaluate()

    filename = f'musicselect{define.musicselect_recognition_version}.res'
    save_resource_serialized(filename, resource, True)
    
    report.report()
