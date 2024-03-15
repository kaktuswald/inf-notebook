from PIL import Image
import json
from sys import exit
from os.path import join,isfile
import numpy as np

from define import define
import data_collection as dc
from resources_larning import larning
from resources_generate import Report,registries_dirname,save_resource_serialized

recognition_define_filename = 'define_recognition_details.json'
recognition_define_filepath = join(registries_dirname, recognition_define_filename)

class Details():
    def __init__(self, np_value, label):
        self.np_value = np_value
        self.label = label

def load_details(labels):
    keys = [key for key in labels.keys() if labels[key]['details'] is not None]

    details = {}
    for key in keys:
        filename = f'{key}.png'
        filepath = join(dc.details_basepath, filename)
        if isfile(filepath):
            image = Image.open(filepath)
            if image.mode != 'RGB':
                continue

            np_value = np.array(image)
            details[key] = Details(np_value, labels[key]['details'])
    
    return details

def load_define():
    try:
        with open(recognition_define_filepath) as f:
            ret = json.load(f)
    except Exception:
        print(f"{recognition_define_filepath}を読み込めませんでした。")
        return None
    
    graphtypes = {}
    for playside in ret['graphtype'].keys():
        graphtypes[playside] = {}
        for graphtype in ret['graphtype'][playside].keys():
            graphtypes[playside][graphtype] = (
                slice(ret['graphtype'][playside][graphtype][0][0], ret['graphtype'][playside][graphtype][0][1]),
                slice(ret['graphtype'][playside][graphtype][1][0], ret['graphtype'][playside][graphtype][1][1]),
                ret['graphtype'][playside][graphtype][2]
            )
    ret['graphtype'] = graphtypes

    option_trims = {}
    for playside in ret['option']['trim'].keys():
        option_trims[playside] = (
            slice(ret['option']['trim'][playside][0][0], ret['option']['trim'][playside][0][1]),
            slice(ret['option']['trim'][playside][1][0], ret['option']['trim'][playside][1][1]),
            ret['option']['trim'][playside][2]
        )
    ret['option']['trim'] = option_trims
    ret['option']['trimlong'] = (
        slice(ret['option']['trimlong'][0][0], ret['option']['trimlong'][0][1], ret['option']['trimlong'][0][2]),
        slice(ret['option']['trimlong'][1][0], ret['option']['trimlong'][1][1], ret['option']['trimlong'][1][2])
    )
    ret['option']['trimshort'] = (
        slice(ret['option']['trimshort'][0][0], ret['option']['trimshort'][0][1], ret['option']['trimshort'][0][2]),
        slice(ret['option']['trimshort'][1][0], ret['option']['trimshort'][1][1], ret['option']['trimshort'][1][2])
    )

    ret['clear_type']['best'] = (
        slice(ret['clear_type']['best'][0][0], ret['clear_type']['best'][0][1]),
        slice(ret['clear_type']['best'][1][0], ret['clear_type']['best'][1][1]),
        ret['clear_type']['best'][2]
    )
    ret['clear_type']['current'] = (
        slice(ret['clear_type']['current'][0][0], ret['clear_type']['current'][0][1]),
        slice(ret['clear_type']['current'][1][0], ret['clear_type']['current'][1][1]),
        ret['clear_type']['current'][2]
    )
    ret['clear_type']['new'] = (
        slice(ret['clear_type']['new'][0][0], ret['clear_type']['new'][0][1]),
        slice(ret['clear_type']['new'][1][0], ret['clear_type']['new'][1][1]),
        ret['clear_type']['new'][2]
    )

    ret['dj_level']['best'] = (
        slice(ret['dj_level']['best'][0][0], ret['dj_level']['best'][0][1]),
        slice(ret['dj_level']['best'][1][0], ret['dj_level']['best'][1][1]),
        ret['dj_level']['best'][2]
    )
    ret['dj_level']['current'] = (
        slice(ret['dj_level']['current'][0][0], ret['dj_level']['current'][0][1]),
        slice(ret['dj_level']['current'][1][0], ret['dj_level']['current'][1][1]),
        ret['dj_level']['current'][2]
    )
    ret['dj_level']['new'] = (
        slice(ret['dj_level']['new'][0][0], ret['dj_level']['new'][0][1]),
        slice(ret['dj_level']['new'][1][0], ret['dj_level']['new'][1][1]),
        ret['dj_level']['new'][2]
    )

    ret['score']['best'] = (
        slice(ret['score']['best'][0][0], ret['score']['best'][0][1]),
        slice(ret['score']['best'][1][0], ret['score']['best'][1][1]),
        ret['score']['best'][2]
    )
    ret['score']['current'] = (
        slice(ret['score']['current'][0][0], ret['score']['current'][0][1]),
        slice(ret['score']['current'][1][0], ret['score']['current'][1][1]),
        ret['score']['current'][2]
    )
    ret['score']['new'] = (
        slice(ret['score']['new'][0][0], ret['score']['new'][0][1]),
        slice(ret['score']['new'][1][0], ret['score']['new'][1][1]),
        ret['score']['new'][2]
    )

    ret['miss_count']['best'] = (
        slice(ret['miss_count']['best'][0][0], ret['miss_count']['best'][0][1]),
        slice(ret['miss_count']['best'][1][0], ret['miss_count']['best'][1][1]),
        ret['miss_count']['best'][2]
    )
    ret['miss_count']['current'] = (
        slice(ret['miss_count']['current'][0][0], ret['miss_count']['current'][0][1]),
        slice(ret['miss_count']['current'][1][0], ret['miss_count']['current'][1][1]),
        ret['miss_count']['current'][2]
    )
    ret['miss_count']['new'] = (
        slice(ret['miss_count']['new'][0][0], ret['miss_count']['new'][0][1]),
        slice(ret['miss_count']['new'][1][0], ret['miss_count']['new'][1][1]),
        ret['miss_count']['new'][2]
    )

    ret['graphtarget']['trimmode'] = (
        slice(ret['graphtarget']['trimmode'][0][0], ret['graphtarget']['trimmode'][0][1]),
        slice(ret['graphtarget']['trimmode'][1][0], ret['graphtarget']['trimmode'][1][1]),
        ret['graphtarget']['trimmode'][2]
    )
    ret['graphtarget']['trimkey'] = (
        ret['graphtarget']['trimkey'][0],
        slice(ret['graphtarget']['trimkey'][1][0], ret['graphtarget']['trimkey'][1][1]),
        ret['graphtarget']['trimkey'][2]
    )

    ret['numberbest']['trim'] = (
        slice(ret['numberbest']['trim'][0][0], ret['numberbest']['trim'][0][1], ret['numberbest']['trim'][0][2]),
        slice(ret['numberbest']['trim'][1][0], ret['numberbest']['trim'][1][1], ret['numberbest']['trim'][1][2])
    )
    ret['numbercurrent']['trim'] = (
        slice(ret['numbercurrent']['trim'][0][0], ret['numbercurrent']['trim'][0][1], ret['numbercurrent']['trim'][0][2]),
        slice(ret['numbercurrent']['trim'][1][0], ret['numbercurrent']['trim'][1][1], ret['numbercurrent']['trim'][1][2])
    )

    return ret

def larning_graphtype(details):
    resourcename = 'graphtype'

    report = Report(resourcename)

    trimareas = details_define['graphtype']

    table = {}
    evaluate_targets = {}
    for key, target in details.items():
        if not 'graphtype' in target.label.keys() or target.label['graphtype'] == '':
            continue
        
        playside = define.details_get_playside(target.np_value)

        if target.label['graphtype'] != 'gauge':
            value = target.label['graphtype']
            trimmed = target.np_value[trimareas[playside][value]]
            if not value in table.keys():
                table[value] = trimmed
                report.saveimage_value(trimmed, f'{value}.png')
                report.append_log(f'({key}({playside})){value}: {trimmed.tolist()}')

        evaluate_targets[key] = target
    
    for key, target in evaluate_targets.items():
        value = target.label['graphtype']

        recoged = 'gauge'
        for k, np_value in table.items():
            playside = define.details_get_playside(target.np_value)
            trimmed = target.np_value[trimareas[playside][k]]
            if np.all(trimmed==np_value):
                recoged = k
        
        if recoged == value:
            report.through()
        else:
            report.saveimage_errorvalue(trimmed, f'{key}.png')
            report.error(f'Mismatch {key} {playside} {recoged} {value}')

    report.report()

    return table

def larning_option(details):
    report = Report('option')

    result ={}
    for k in ['options_arrange', 'options_arrange_dp', 'options_arrange_sync', 'options_flip', 'options_assist']:
        for v in define.value_list[k]:
            result[v] = []
    result['BATTLE'] = []
    lengths = [details_define['option']['width'][value]//16*8 for value in result.keys()]
    sorted_lengths = sorted(set(lengths))
    sorted_lengths.reverse()
    max_length = sorted_lengths[0]

    def generatekey(np_value):
        bins = np.where(np_value[:, ::4]==details_define['option']['maskvalue'], 1, 0).T
        hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
        return ''.join([format(v, '0x') for v in hexs.flatten()])

    def registerkey(key, value, trimmed, side=''):
        tablekey = generatekey(trimmed[:, :trimmed.shape[1]//16*16])
        if not tablekey in result[value]:
            result[value].append(tablekey)
            report.saveimage_value(trimmed, f'{value}_{key}_{side}.png')
        if not tablekey in table:
            table[tablekey] = value

    table = {'lengths': sorted_lengths}
    evaluate_targets = {}
    for key, target in details.items():
        if not 'graphtype' in target.label.keys() or target.label['graphtype'] != 'gauge':
            continue

        playside = define.details_get_playside(target.np_value)
        trimmed = target.np_value[details_define['option']['trim'][playside]]

        if target.label['option_battle']:
            value = 'BATTLE'
            trimmed_once = trimmed[:, :details_define['option']['width'][value]]
            registerkey(key, value, trimmed_once)
            trimmed = trimmed[:, details_define['option']['width'][value] + details_define['option']['width'][',']:]
        
        if target.label['option_arrange'] != '':
            value = target.label['option_arrange']
            trimmed_once = trimmed[:, :details_define['option']['width'][value]]
            registerkey(key, value, trimmed_once)
            trimmed = trimmed[:, details_define['option']['width'][value] + details_define['option']['width'][',']:]

        if target.label['option_arrange_dp'] != '/':
            left, right = target.label['option_arrange_dp'].split('/')
            for side, value, delimiter in [['left', left, '/'], ['right', right, ',']]:
                trimmed_once = trimmed[:, :details_define['option']['width'][value]]
                registerkey(key, value, trimmed_once, side)
                trimmed = trimmed[:, details_define['option']['width'][value] + details_define['option']['width'][delimiter]:]

        if target.label['option_arrange_sync'] != '':
            value = target.label['option_arrange_sync']
            trimmed_once = trimmed[:, :details_define['option']['width'][value]]
            registerkey(key, value, trimmed_once)
            trimmed = trimmed[:, details_define['option']['width'][value] + details_define['option']['width'][',']:]

        if target.label['option_flip'] != '':
            value = target.label['option_flip']
            trimmed_once = trimmed[:, :details_define['option']['width'][value]]
            registerkey(key, value, trimmed_once)
            trimmed = trimmed[:, details_define['option']['width'][value] + details_define['option']['width'][',']:]

        if target.label['option_assist'] != '':
            value = target.label['option_assist']
            trimmed_once = trimmed[:, :details_define['option']['width'][value]]
            registerkey(key, value, trimmed_once)
            trimmed = trimmed[:, details_define['option']['width'][value] + details_define['option']['width'][',']:]

        evaluate_targets[key] = target
    
    for key, tablekeys in result.items():
        report.append_log(f'{key}: {tablekeys}')
    
    report.append_log(f'Option count: {len(result)}')
    report.append_log(f'Key count: {len(table)}')

    for key, target in evaluate_targets.items():
        playside = define.details_get_playside(target.np_value)
        trimmed = target.np_value[details_define['option']['trim'][playside]]
        res = {'arrange': '', 'arrange_dp': '/', 'arrange_sync': '', 'flip': '', 'assist': '', 'battle': False}
        while True:
            tablekey = generatekey(trimmed[:, :max_length*2])
            value = None
            for length in sorted_lengths:
                trimkey = tablekey[:length]
                if trimkey in table.keys():
                    value = table[trimkey]
                    break
            
            if value is None:
                break

            arrange_dp_left = False
            if value in define.value_list['options_arrange']:
                res['arrange'] = value
            if value in define.value_list['options_arrange_dp']:
                if res['arrange_dp'] == '/':
                    res['arrange_dp'] = f'{value}/'
                    arrange_dp_left = True
                else:
                    res['arrange_dp'] += value
            if value in define.value_list['options_arrange_sync']:
                res['arrange_sync'] = value
            if value in define.value_list['options_flip']:
                res['flip'] = value
            if value in define.value_list['options_assist']:
                res['assist'] = value
            if value == 'BATTLE':
                res['battle'] = True
            if not arrange_dp_left:
                trimmed = trimmed[:, details_define['option']['width'][value] + details_define['option']['width'][',']:]
            else:
                trimmed = trimmed[:, details_define['option']['width'][value] + details_define['option']['width']['/']:]
        
        evaluate = [
            res['arrange'] == target.label['option_arrange'],
            res['arrange_dp'] == target.label['option_arrange_dp'],
            res['arrange_sync'] == target.label['option_arrange_sync'],
            res['flip'] == target.label['option_flip'],
            res['assist'] == target.label['option_assist'],
            res['battle'] == target.label['option_battle']
        ]
        if not False in evaluate:
            report.through()
        else:
            report.error(f'Mismatch option {key} {evaluate} {res}')

    report.report()

    print(table)
    return table

def larning_cleartype(details):
    resourcename = 'cleartype'

    report = Report(resourcename)

    table = {}
    evaluate_targets = {}
    for key, target in details.items():
        if 'clear_type_best' in target.label.keys() and target.label['clear_type_best'] != "":
            value = target.label['clear_type_best']
            trimmed = target.np_value[details_define['clear_type']['best']]
            uniques, counts = np.unique(trimmed, return_counts=True)
            color = uniques[np.argmax(counts)]
            table[color] = value
        
        if 'clear_type_current' in target.label.keys() and target.label['clear_type_current'] != "":
            value = target.label['clear_type_current']
            trimmed = target.np_value[details_define['clear_type']['current']]
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
        if 'clear_type_best' in target.label.keys() and target.label['clear_type_best'] != "":
            trimmed = target.np_value[details_define['clear_type']['best']]
            uniques, counts = np.unique(trimmed, return_counts=True)
            color = uniques[np.argmax(counts)]

            result = None
            if color in table.keys():
                result = table[color]
            
            if target.label['clear_type_best'] == result:
                report.through()
            else:
                report.saveimage_errorvalue(trimmed, f'{key}-best.png')
                report.error(f'Mismatch best {result} {key}')

        if 'clear_type_current' in target.label.keys() and target.label['clear_type_current'] != "":
            trimmed = target.np_value[details_define['clear_type']['current']]
            uniques, counts = np.unique(trimmed, return_counts=True)
            color = uniques[np.argmax(counts)]

            result = None
            if color in table.keys():
                result = table[color]
            
            if target.label['clear_type_current'] == result:
                report.through()
            else:
                report.saveimage_errorvalue(trimmed, f'{key}-current.png')
                report.error(f'Mismatch current {result} {key}')

    report.report()

    return table

def larning_djlevel(details):
    resourcename = 'djlevel'

    report = Report(resourcename)

    table = {}
    evaluate_targets = {}
    for key, target in details.items():
        if not 'dj_level_best' in target.label.keys() or target.label['dj_level_best'] == "":
            continue
        if not 'dj_level_current' in target.label.keys() or target.label['dj_level_current'] == "":
            continue

        if 'dj_level_best' in target.label.keys() and target.label['dj_level_best'] != "":
            value = target.label['dj_level_best']
            trimmed = target.np_value[details_define['dj_level']['best']]
            count = np.count_nonzero(trimmed==details_define['dj_level']['maskvalue'])
            table[count] = value
        
        if 'dj_level_current' in target.label.keys() and target.label['dj_level_current'] != "":
            value = target.label['dj_level_current']
            trimmed = target.np_value[details_define['dj_level']['current']]
            count = np.count_nonzero(trimmed==details_define['dj_level']['maskvalue'])
            table[count] = value

        evaluate_targets[key] = target
    
    for value in define.value_list['dj_levels']:
        keys = [k for k, v in table.items() if v == value]
        if not len(keys):
            report.append_log(f'Not found key {value}')
        report.append_log(f'{value}: {keys}')

    for key, target in evaluate_targets.items():
        if 'dj_level_best' in target.label.keys() and target.label['dj_level_best'] != "":
            trimmed = target.np_value[details_define['dj_level']['best']]
            count = np.count_nonzero(trimmed==details_define['dj_level']['maskvalue'])

            result = None
            if count in table.keys():
                result = table[count]
            
            if target.label['dj_level_best'] == result:
                report.through()
            else:
                report.saveimage_errorvalue(trimmed, f'{key}-best.png')
                report.error(f'Mismatch best {result} {key}({count})')

        if 'dj_level_current' in target.label.keys() and target.label['dj_level_current'] != "":
            trimmed = target.np_value[details_define['dj_level']['current']]
            count = np.count_nonzero(trimmed==details_define['dj_level']['maskvalue'])

            result = None
            if count in table.keys():
                result = table[count]
            
            if target.label['dj_level_current'] == result:
                report.through()
            else:
                report.saveimage_errorvalue(trimmed, f'{key}-current.png')
                report.error(f'Mismatch current {result} {key}({count})')

    report.report()

    return table

def larning_numberbest(details):
    resourcename = 'numberbest'

    report = Report(resourcename)

    table = {}
    evaluate_targets = {}
    for key, target in details.items():
        if 'score_best' in target.label.keys() and target.label['score_best'] != "":
            value = int(target.label['score_best']) % 10
            trimmed = target.np_value[details_define['score']['best']]
            splitted = np.hsplit(trimmed, details_define['score']['digit'])
            trimmed_once = splitted[-1][details_define['numberbest']['trim']]
            bins = np.where(trimmed_once==details_define['numberbest']['maskvalue'], 1, 0).T
            hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
            tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
            if not tablekey in table or not value in table.values():
                report.saveimage_value(trimmed_once, f'{value}-{key}-score.png')
                table[tablekey] = value

            evaluate_targets[f'score_{key}'] = target

        if 'miss_count_best' in target.label.keys() and target.label['miss_count_best'] != "":
            value = int(target.label['miss_count_best']) % 10
            trimmed = target.np_value[details_define['miss_count']['best']]
            splitted = np.hsplit(trimmed, details_define['miss_count']['digit'])
            trimmed_once = splitted[-1][details_define['numberbest']['trim']]
            bins = np.where(trimmed_once==details_define['numberbest']['maskvalue'], 1, 0).T
            hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
            tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
            if not tablekey in table or not value in table.values():
                report.saveimage_value(trimmed_once, f'{value}-{key}-misscount.png')
                table[tablekey] = value
        
            evaluate_targets[f'miss_count_{key}'] = target
    
    for value in range(10):
        keys = [k for k, v in table.items() if v == value]
        if not len(keys):
            report.append_log(f'Not found key {value}')
        else:
            report.append_log(f'{value}: {keys}')

    for key, target in evaluate_targets.items():
        if 'score_best' in target.label.keys() and target.label['score_best'] != "":
            trimmed = target.np_value[details_define['score']['best']]

            result = 0
            keys = []
            for dig in range(details_define['score']['digit']):
                splitted = np.hsplit(trimmed, details_define['score']['digit'])
                trimmed_once = splitted[-(dig+1)][details_define['numberbest']['trim']]
                bins = np.where(trimmed_once==details_define['numberbest']['maskvalue'], 1, 0).T
                hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
                tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
                keys.append(tablekey)
                if not tablekey in table.keys():
                    break
                result += 10 ** dig * table[tablekey]
            
            if int(target.label['score_best']) == result:
                report.through()
            else:
                report.saveimage_errorvalue(trimmed, f'{key}.png')
                report.error(f"Mismatch score {result} {target.label['score_best']}")
                report.error(f'{keys}')

        if 'miss_count_best' in target.label.keys() and target.label['miss_count_best'] != "":
            trimmed = target.np_value[details_define['miss_count']['best']]

            result = 0
            for dig in range(details_define['miss_count']['digit']):
                splitted = np.hsplit(trimmed, details_define['miss_count']['digit'])
                trimmed_once = splitted[-(dig+1)][details_define['numberbest']['trim']]
                bins = np.where(trimmed_once==details_define['numberbest']['maskvalue'], 1, 0).T
                hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
                tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
                if not tablekey in table.keys():
                    break
                result += 10 ** dig * table[tablekey]
            
            if int(target.label['miss_count_best']) == result:
                report.through()
            else:
                report.saveimage_errorvalue(trimmed, f'{key}.png')
                report.error(f"Mismatch miss count {result} {target.label['miss_count_best']}")

    report.report()

    return table

def larning_numbercurrent(details):
    resourcename = 'numbercurrent'

    report = Report(resourcename)

    table = {}
    evaluate_targets = {}
    for key, target in details.items():
        if 'score_current' in target.label.keys() and target.label['score_current'] != "":
            value = int(target.label['score_current']) % 10
            trimmed = target.np_value[details_define['score']['current']]
            splitted = np.hsplit(trimmed, details_define['score']['digit'])
            trimmed_once = splitted[-1][details_define['numbercurrent']['trim']]
            bins = np.where(trimmed_once==details_define['numbercurrent']['maskvalue'], 1, 0).T
            hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
            tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
            if not tablekey in table or not value in table.values():
                report.saveimage_value(trimmed_once, f'{value}-{key}-score.png')
                table[tablekey] = value

            evaluate_targets[f'score_{key}'] = target

        if 'miss_count_current' in target.label.keys() and target.label['miss_count_current'] != "":
            value = int(target.label['miss_count_current']) % 10
            trimmed = target.np_value[details_define['miss_count']['current']]
            splitted = np.hsplit(trimmed, details_define['miss_count']['digit'])
            trimmed_once = splitted[-1][details_define['numbercurrent']['trim']]
            bins = np.where(trimmed_once==details_define['numbercurrent']['maskvalue'], 1, 0).T
            hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
            tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
            if not tablekey in table or not value in table.values():
                report.saveimage_value(trimmed_once, f'{value}-{key}-misscount.png')
                table[tablekey] = value
        
            evaluate_targets[f'miss_count_{key}'] = target
    
    for value in range(10):
        keys = [k for k, v in table.items() if v == value]
        if not len(keys):
            report.append_log(f'Not found key {value}')
        else:
            report.append_log(f'{value}: {keys}')

    for key, target in evaluate_targets.items():
        if 'score_current' in target.label.keys() and target.label['score_current'] != "":
            trimmed = target.np_value[details_define['score']['current']]

            result = 0
            keys = []
            for dig in range(details_define['score']['digit']):
                splitted = np.hsplit(trimmed, details_define['score']['digit'])
                trimmed_once = splitted[-(dig+1)][details_define['numbercurrent']['trim']]
                bins = np.where(trimmed_once==details_define['numbercurrent']['maskvalue'], 1, 0).T
                hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
                tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
                keys.append(tablekey)
                if not tablekey in table.keys():
                    break
                result += 10 ** dig * table[tablekey]
            
            if int(target.label['score_current']) == result:
                report.through()
            else:
                report.saveimage_errorvalue(trimmed, f'{key}.png')
                report.error(f"Mismatch score {result} {target.label['score_current']}")
                report.error(f'{keys}')

        if 'miss_count_current' in target.label.keys() and target.label['miss_count_current'] != "":
            trimmed = target.np_value[details_define['miss_count']['current']]

            result = 0
            for dig in range(details_define['miss_count']['digit']):
                splitted = np.hsplit(trimmed, details_define['miss_count']['digit'])
                trimmed_once = splitted[-(dig+1)][details_define['numbercurrent']['trim']]
                bins = np.where(trimmed_once==details_define['numbercurrent']['maskvalue'], 1, 0).T
                hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
                tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])
                if not tablekey in table.keys():
                    break
                result += 10 ** dig * table[tablekey]
            
            if int(target.label['miss_count_current']) == result:
                report.through()
            else:
                report.saveimage_errorvalue(trimmed, f'{key}.png')
                report.error(f"Mismatch miss count {result} {target.label['miss_count_current']}")

    report.report()

    return table

def larning_not_new(details):
    report = Report('notnew')

    trimareas = {}
    for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
        trimareas[key] = details_define[key]['new']

    larning_targets = {}
    evaluate_targets = {}
    for key, target in details.items():
        for k in ['clear_type', 'dj_level', 'score', 'miss_count']:
            if not f'{k}_new' in target.label.keys() or target.label[f'{k}_new'] is True:
                continue

            trimmed = target.np_value[trimareas[k]]
            larning_targets[f'{key}_{k}.png'] = trimmed

        evaluate_targets[key] = target
    
    report.append_log(f'source count: {len(larning_targets)}')

    result = larning(larning_targets, report)
    if result is None:
        report.report()
        return

    for key, target in evaluate_targets.items():
        for k in ['clear_type', 'dj_level', 'score', 'miss_count']:
            is_new = target.label[f'{k}_new']
            trimmed = target.np_value[trimareas[k]]
            recoged = np.all((result==0)|(trimmed==result))
            if (recoged and not is_new) or (not recoged and is_new):
                report.through()
            else:
                report.saveimage_errorvalue(trimmed, f'{key}_{k}.png')
                report.error(f'Mismatch {k}_new {is_new} {recoged} {key}')

    report.report()

    return result

def larning_graphtarget(details):
    report = Report('graphtarget')

    trimareas = details_define['graphtarget']

    table = {}
    evaluate_targets = {}
    result = {}
    for key, target in details.items():
        if not 'graphtarget' in target.label.keys() or target.label['graphtarget'] == '':
            continue

        value = target.label['graphtarget']

        trimmed = target.np_value[trimareas['trimmode']]
        uniques, counts = np.unique(trimmed, return_counts=True)
        mode = uniques[np.argmax(counts)]
        if not mode in table.keys():
            table[mode] = {}

        trimmed = target.np_value[trimareas['trimkey']]
        bins = np.where(trimmed==mode, 1, 0)
        hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
        tablekey = ''.join([format(v, '0x') for v in hexs])
        if not tablekey in table[mode].keys():
            table[mode][tablekey] = value
            report.saveimage_value(trimmed, f'{value}.png')
            result[value] = f'({key}){mode} {tablekey}'

        evaluate_targets[key] = target
    
    for key, target in evaluate_targets.items():
        value = target.label['graphtarget']

        recoged = None

        np_value = target.np_value[trimareas['trimmode']]
        uniques, counts = np.unique(np_value, return_counts=True)
        mode = uniques[np.argmax(counts)]
        if mode in table.keys():
            np_value = target.np_value[trimareas['trimkey']]
            bins = np.where(np_value==mode, 1, 0)
            hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
            tablekey = ''.join([format(v, '0x') for v in hexs])
            if tablekey in table[mode].keys():
                recoged = table[mode][tablekey]

        if recoged == value:
            report.through()
        else:
            report.saveimage_errorvalue(np_value, f'{key}.png')
            report.error(f'Mismatch {recoged} {value} {key}')

    for value in define.value_list['graphtargets']:
        if value in result.keys():
            report.append_log(f'{value}: {result[value]}')
        else:
            report.append_log(f'{value}: Not define.')
            report.error(f'Not define {value}')

    report.report()

    return table

if __name__ == '__main__':
    try:
        with open(dc.label_filepath) as f:
            labels = json.load(f)
    except Exception:
        print(f"{dc.label_filepath}を読み込めませんでした。")
        exit()
    
    details_define = load_define()
    if details_define is None:
        exit()

    details = load_details(labels)
    
    table_graphtype = larning_graphtype(details)
    table_option = larning_option(details)
    table_clear_type = larning_cleartype(details)
    table_dj_level = larning_djlevel(details)
    table_number_best = larning_numberbest(details)
    table_number_current = larning_numbercurrent(details)
    mask_not_new = larning_not_new(details)
    table_graphtarget = larning_graphtarget(details)
 
    filename = f'details{define.details_recognition_version}.res'
    save_resource_serialized(filename, {
        'define': details_define,
        'graphtype': table_graphtype,
        'option': table_option,
        'clear_type': table_clear_type,
        'dj_level': table_dj_level,
        'number_best': table_number_best,
        'number_current': table_number_current,
        'not_new': mask_not_new,
        'graphtarget': table_graphtarget
    })
