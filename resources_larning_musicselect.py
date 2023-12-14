from PIL import Image
import json
from sys import exit
from os.path import join,isfile
import numpy as np

from define import define
from raw_image import raws_basepath
from resources_generate import Report,save_resource_serialized,registries_dirname,report_dirname
from resources_larning import larning_multivalue

label_filepath = join(raws_basepath, 'label_musicselect.json')

recognition_define_filename = 'define_recognition_musicselect.json'
recognition_define_filepath = join(registries_dirname, recognition_define_filename)

report_basedir_musicrecog = join(report_dirname, 'musicrecog')
report_basedir_musictable = join(report_dirname, 'musictable')

class ImageValues():
    def __init__(self, np_value, label):
        self.np_value = np_value
        self.label = label

def load_images(labels):
    keys = [key for key in labels.keys()]

    imagevaleus = {}
    for filename in keys:
        filepath = join(raws_basepath, filename)
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
        if not 'playmode' in target.label.keys():
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
        if 'difficulty' in target.label.keys() and target.label['difficulty'] == '':
            continue
        evaluate_targets[key] = target
        for difficulty in difficulties:
            level_key = f'level_{difficulty}'
            if level_key in target.label.keys() and target.label[level_key] == '':
                continue
            if str.upper(difficulty) == target.label['difficulty']:
                targets['select'][difficulty][key] = target
            else:
                targets['noselect'][difficulty][key] = target

    for difficulty in difficulties:
        define_target = musicselect_define['levels']['select'][difficulty]

        trim = (
            slice(define_target['trim'][0][0], define_target['trim'][0][1]),
            slice(define_target['trim'][1][0], define_target['trim'][1][1]),
            define_target['trim'][2]
        )
        maskvalue = define_target['maskvalue']
        table = {}

        for key, target in targets['select'][difficulty].items():
            level_key = f'level_{difficulty}'
            value = target.label[level_key]
            trimmed = target.np_value[trim]
            bins = np.where(trimmed==maskvalue, 1, 0)
            hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
            tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
            if tablekey in table.keys() and value != table[tablekey]:
                report.error(f'Duplicate select {difficulty} {tablekey} {value} {table[tablekey]}')
            table[tablekey] = value

        resource['levels']['select'][difficulty] = {
            'trim': trim,
            'maskvalue': maskvalue,
            'table': table
        }

    for difficulty in difficulties:
        define_target = musicselect_define['levels']['noselect'][difficulty]

        trim = (
            slice(define_target['trim'][0][0], define_target['trim'][0][1]),
            slice(define_target['trim'][1][0], define_target['trim'][1][1])
        )
        maskvalue = define_target['maskvalue']
        table = {}

        for key, target in targets['noselect'][difficulty].items():
            level_key = f'level_{difficulty}'
            value = target.label[level_key]
            trimmed = target.np_value[trim]
            bins = np.where((trimmed[:,:,0]==trimmed[:,:,1])&(trimmed[:,:,0]==trimmed[:,:,2])&(trimmed[:,:,0]==maskvalue), 1, 0)
            hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
            tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
            if tablekey in table.keys() and value != table[tablekey]:
                report.error(f'Duplicate noselect {difficulty} {tablekey} {value} {table[tablekey]}')
            table[tablekey] = value

        resource['levels']['noselect'][difficulty] = {
            'trim': trim,
            'maskvalue': maskvalue,
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
                    bins = np.where(trimmed==resource['levels'][selectstate][difficulty]['maskvalue'], 1, 0)
                    hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
                    tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
                if selectstate == 'noselect':
                    trimmed = target.np_value[resource['levels'][selectstate][difficulty]['trim']]
                    bins = np.where((trimmed[:,:,0]==trimmed[:,:,1])&(trimmed[:,:,0]==trimmed[:,:,2])&(trimmed[:,:,0]==resource['levels'][selectstate][difficulty]['maskvalue']), 1, 0)
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
        
            evaluate_targets[f'miss_count_{key}'] = target
    
    for value in range(10):
        keys = [k for k, v in table.items() if v == value]
        if not len(keys):
            report.append_log(f'Not found key {value}')
        else:
            report.append_log(f'{value}: {keys}')

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
                report.error(f'{keys}')

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

    arcade_slicevalue = (arcade['area'][1][1] - arcade['area'][1][0], 1)

    resource_target['arcade'] = {
        'area': (
            slice(arcade['area'][0][0], arcade['area'][0][1]),
            slice(arcade['area'][1][0], arcade['area'][1][1]),
            arcade['area'][2]
        ),
        'masks': [np.tile(np.array(m), arcade_slicevalue).T for m in arcade['masks']]
    }

    resource_target['infinitas'] = {
        'area': (
            slice(infinitas['area'][0][0], infinitas['area'][0][1]),
            slice(infinitas['area'][1][0], infinitas['area'][1][1]),
            infinitas['area'][2]
        ),
        'maskvalues': infinitas['maskvalues']
    }

    resource_target['leggendaria'] = {
        'area': (
            slice(leggendaria['area'][0][0], leggendaria['area'][0][1]),
            slice(leggendaria['area'][1][0], leggendaria['area'][1][1]),
            leggendaria['area'][2]
        ),
        'maskvalue': leggendaria['maskvalue']
    }

def larning_musicname_arcade(targets, report):
    resource_target = resource['musicname']['arcade']

    table = resource_target['table'] = {}

    for key, target in targets.items():
        if False:
            if key != '20231210-203050-697158.png':
                continue
            v = target.np_value[199:251, 667:668]
            v2 = np.where((v[:,:,0]==v[:,:,1])&(v[:,:,0]==v[:,:,2]),v[:,:,0],0)
            v3 = ','.join(map(str, v2.flatten().tolist()))
            print(v3)
            break

        cropped = target.np_value[resource_target['area']]
        counts = [np.count_nonzero(np.where(cropped==mask, cropped, 0)) for mask in resource_target['masks']]
        recogkey = max(counts)

        musicname = target.label['musicname']

        report.append_log(f'{key}: arcade {musicname} {counts}')
        if(recogkey == 0):
            report.error(f'{key}: no value arcade {musicname} {counts}')
            report.saveimage_errorvalue(cropped, f'maskerror-{key}')
        else:
            table[recogkey] = target.label['musicname']

def larning_musicname_infinitas(targets, report):
    resource_target = resource['musicname']['infinitas']

    table = resource_target['table'] = {}

    for key, target in targets.items():
        musicname = target.label['musicname']

        cropped = target.np_value[resource_target['area']]
        maskeds = [np.where(cropped==maskvalue, cropped, 0) for maskvalue in resource_target['maskvalues']]
        counts = [np.count_nonzero(v) for v in maskeds]
        recogkey = max(counts)

        report.append_log(f'{key}: infinitas {musicname} {recogkey}')
        if(recogkey == 0):
            report.error(f'{key}: no value infinitas {musicname} {recogkey}')
            report.saveimage_errorvalue(cropped, f'maskerror-{key}')
        else:
            table[recogkey] = target.label['musicname']

def larning_musicname_leggendaria(targets, report):
    resource_target = resource['musicname']['leggendaria']

    table = resource_target['table'] = {}

    for key, target in targets.items():
        musicname = target.label['musicname']

        cropped = target.np_value[resource_target['area']]
        masked = np.where(cropped == resource_target['maskvalue'], cropped, 0)
        recogkey = np.count_nonzero(masked)
        
        report.append_log(f'{key}: leggendaria {musicname} {recogkey}')
        if(recogkey == 0):
            report.error(f'{key}: no value leggendaria {musicname} {recogkey}')
            report.saveimage_errorvalue(cropped, f'maskerror-{key}')
        else:
            table[recogkey] = target.label['musicname']

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
            resource_target = resource['musicname']['arcade']
            cropped = target.np_value[resource_target['area']]
            counts = [np.count_nonzero(np.where(cropped==mask, cropped, 0)) for mask in resource_target['masks']]
            key = max(counts)
            if key in resource_target['table'].keys():
                resultmusicname = resource_target['table'][key]
    
        if resultmusicname is None:
            resource_target = resource['musicname']['infinitas']
            cropped = target.np_value[resource_target['area']]
            maskeds = [np.where(cropped==maskvalue, cropped, 0) for maskvalue in resource_target['maskvalues']]
            counts = [np.count_nonzero(v) for v in maskeds]
            key = max(counts)
            if key in resource_target['table'].keys():
                resultmusicname = resource_target['table'][max(counts)]
        
        if resultmusicname is None:
            resource_target = resource['musicname']['leggendaria']
            cropped = target.np_value[resource_target['area']]
            masked = np.where(cropped==resource_target['maskvalue'], cropped, 0)
            key = np.count_nonzero(masked)
            if key in resource_target['table'].keys():
                resultmusicname = resource_target['table'][key]

        if(musicname == resultmusicname):
            report.through()
        else:
            report.error(f'{key}: wrong recognition {musicname} {resultmusicname}')
            report.saveimage_errorvalue(cropped, f'maskerror-{key}')

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

    imagevalues = load_images(labels)
    
    resource = {}

    larning_playmode()
    larning_levels()
    larning_cleartype()
    larning_djlevel()
    larning_number()
    larning_musicname()

    filename = f'musicselect{define.musicselect_recognition_version}.res'
    save_resource_serialized(filename, resource)
