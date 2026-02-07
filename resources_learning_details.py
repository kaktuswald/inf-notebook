from PIL import Image
import json
from sys import exit
from os import mkdir
from os.path import join,isfile,exists
import numpy as np

from define import define,Graphtypes
import data_collection as dc
from resources_learning import learning
from resources_generate import Report,save_resource_serialized,registries_dirname,report_dirname

recognition_define_filename = 'define_recognition_details.json'
recognition_define_filepath = join(registries_dirname, recognition_define_filename)

report_basedir_option = join(report_dirname, 'option')

class Details():
    def __init__(self, np_value, label):
        self.np_value = np_value
        self.label = label

def load_details(labels):
    def is_using(key):
        if not 'details' in labels[key].keys() or labels[key]['details'] is None:
            return False
        if not 'ignore' in labels[key]['details']:
            return True
        
        return not labels[key]['details']['ignore']
    
    keys = [key for key in labels.keys() if is_using(key)]

    details = {}
    for key in keys:
        filename = f'{key}.png'
        filepath = join(dc.details_basepath, filename)
        if isfile(filepath):
            image = Image.open(filepath)
            if image.mode != 'RGB':
                continue

            np_value = np.array(image, dtype=np.uint8)
            details[key] = Details(np_value, labels[key]['details'])
    
    return details

def load_define():
    try:
        with open(recognition_define_filepath) as f:
            ret = json.load(f)
    except Exception:
        print(f"{recognition_define_filepath}を読み込めませんでした。")
        return None
    
    if not 'resourceversion' in ret.keys() or ret['resourceversion'] != define.details_recognition_version:
        print(f"{recognition_define_filepath}のリソースバージョンが一致しません。")
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

    for playside in ret['useoption']['trim'].keys():
        ret['useoption']['trim'][playside] = (
            slice(ret['useoption']['trim'][playside][0][0], ret['useoption']['trim'][playside][0][1]),
            slice(ret['useoption']['trim'][playside][1][0], ret['useoption']['trim'][playside][1][1]),
            ret['useoption']['trim'][playside][2]
        )

    for playside in ret['option']['trim'].keys():
        ret['option']['trim'][playside] = (
            slice(
                ret['option']['trim'][playside][0][0],
                ret['option']['trim'][playside][0][1],
            ),
            slice(
                ret['option']['trim'][playside][1][0],
                ret['option']['trim'][playside][1][1],
                ret['option']['trim'][playside][1][2],
            ),
            ret['option']['trim'][playside][2]
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

def learning_graphtype(details):
    resourcename = 'graphtype'

    report = Report(resourcename)

    trimareas = details_define['graphtype']

    table = {}
    evaluate_targets = {}
    for key, target in details.items():
        if not 'graphtype' in target.label.keys() or target.label['graphtype'] == '':
            continue
        
        playside = define.details_get_playside(target.np_value)

        if target.label['graphtype'] != Graphtypes.GAUGE:
            value = target.label['graphtype']
            trimmed = target.np_value[trimareas[playside][value]]
            if not value in table.keys():
                table[value] = trimmed
                report.saveimage_value(trimmed, f'{value}.png')
                report.append_log(f'({key}({playside})){value}: {trimmed.tolist()}')

        evaluate_targets[key] = target
    
    for key, target in evaluate_targets.items():
        value = target.label['graphtype']

        recoged = Graphtypes.GAUGE
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

def learning_option(details: dict[str, Details]):
    resourcename = 'option'

    report = Report(resourcename)
    
    values = [None]

    for assist in (None, *define.value_list['options_assist']):
        for sp_arrange in define.value_list['options_arrange']:
            values.append(','.join(v for v in (sp_arrange, assist, ) if v is not None))

    for battle in (None, 'BATTLE'):
        for flip in (None, *define.value_list['options_flip']):
            if battle is not None and flip is not None:
                continue

            for assist in (None, *define.value_list['options_assist']):
                for left_arrange in define.value_list['options_arrange_dp']:
                    for right_arrange in define.value_list['options_arrange_dp']:
                        if left_arrange == 'S-RAN' and right_arrange == 'H-RAN':
                            continue
                        if left_arrange == 'H-RAN' and right_arrange == 'S-RAN':
                            continue

                        arrange = None
                        if left_arrange != 'OFF' or right_arrange != 'OFF':
                            arrange = f'{left_arrange}/{right_arrange}'

                        if battle is None and arrange is None and flip is None and assist is None:
                            continue

                        values.append(','.join(v for v in (battle, arrange, flip, assist, ) if v is not None))

                if battle is not None and flip is None:
                    for sync_arrange in define.value_list['options_arrange_sync']:
                        values.append(','.join(v for v in (battle, sync_arrange, flip, assist, ) if v is not None))
    
    keyresult = {}
    for value in values:
        keyresult[value] = {}
        for playside in define.value_list['play_sides']:
            keyresult[value][playside] = {}
    
    useoptioncounts = []
    table = {}
    evaluate_targets = {}
    for key, target in details.items():
        if not 'option_arrange' in target.label.keys():
            continue
        if not 'option_arrange_dp' in target.label.keys():
            continue
        if not 'option_arrange_sync' in target.label.keys():
            continue
        if not 'option_flip' in target.label.keys():
            continue
        if not 'option_assist' in target.label.keys():
            continue
        if not 'option_battle' in target.label.keys():
            continue

        playside = define.details_get_playside(target.np_value)

        useoptiontrimmed = target.np_value[details_define['useoption']['trim'][playside]]
        useoptioncount = np.count_nonzero(useoptiontrimmed==details_define['useoption']['maskvalue'])
        useoptionresult = str(useoptioncount)
        if useoptioncount != 0 and not useoptionresult in useoptioncounts:
            useoptioncounts.append(useoptionresult)

        options = (
            'BATTLE' if target.label['option_battle'] else None,
            target.label['option_arrange'] if target.label['option_arrange'] is not None and len(target.label['option_arrange']) else None,
            target.label['option_arrange_dp'] if target.label['option_arrange_dp'] != '/' else None,
            target.label['option_arrange_sync'] if target.label['option_arrange_sync'] is not None and len(target.label['option_arrange_sync']) else None,
            target.label['option_flip'] if target.label['option_flip'] is not None and len(target.label['option_flip']) else None,
            target.label['option_assist'] if target.label['option_assist'] is not None and len(target.label['option_assist']) else None,
        )

        value = ','.join((v for v in options if v is not None and len(v)))
        if len(value) == 0:
            value = None

        if not value in values:
            report.error(f'Abnormal value: {value}')
            continue

        trimmed = target.np_value[details_define['option']['trim'][playside]]
        bins = np.where(trimmed>=details_define['option']['thresholdlower'], 1, 0)
        hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
        tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])

        if not tablekey in table.keys():
            table[tablekey] = value
        
        if not tablekey in keyresult[value][playside].keys():
            keyresult[value][playside][tablekey] = key
            if value is not None:
                report.saveimage_value(trimmed>=details_define['option']['thresholdlower'], f'{value.replace('/', '_')}-{key}.png')

        evaluate_targets[key] = target
    
    report.append_log('')

    report.append_log(','.join(useoptioncounts))
    if len(useoptioncounts) == 0:
        report.error(f'Use option value is none')
    if len(useoptioncounts) > 1:
        report.error(f'Use option value is duplicate: {useoptioncounts}')

    for key, target in evaluate_targets.items():
        playside = define.details_get_playside(target.np_value)

        trimmed = target.np_value[details_define['option']['trim'][playside]]
        bins = np.where(trimmed>=details_define['option']['thresholdlower'], 1, 0)
        hexs = bins[:,0::4]*8+bins[:,1::4]*4+bins[:,2::4]*2+bins[:,3::4]
        tablekey = ''.join([format(v, '0x') for v in hexs.flatten()])

        result = None
        if tablekey in table.keys():
            result = table[tablekey]
        
        options = (
            'BATTLE' if target.label['option_battle'] else None,
            target.label['option_arrange'] if target.label['option_arrange'] is not None and len(target.label['option_arrange']) else None,
            target.label['option_arrange_dp'] if target.label['option_arrange_dp'] != '/' else None,
            target.label['option_arrange_sync'] if target.label['option_arrange_sync'] is not None and len(target.label['option_arrange_sync']) else None,
            target.label['option_flip'] if target.label['option_flip'] is not None and len(target.label['option_flip']) else None,
            target.label['option_assist'] if target.label['option_assist'] is not None and len(target.label['option_assist']) else None,
        )

        value = ','.join((v for v in options if v is not None))
        if len(value) == 0:
            value = None

        if value == result:
            report.through()
        else:
            report.saveimage_errorvalue(trimmed, f'[Error]{value.replace('/', '_')}-{key}.png')
            report.error(f'Mismatch {result} {key}')

    report_keys = []
    report_keycompare = []
    for value in values:
        report_keys.append(f'{value}:')
        for playside in define.value_list['play_sides']:
            report_keys.append(f'\t{playside}:')
            tablekeys = [*keyresult[value][playside].keys()]
            for tablekey in tablekeys:
                report_keys.append(f'\t\t{tablekey}: {keyresult[value][playside][tablekey]}')
            if len(tablekeys) == 0:
                report.error(f'Not key: {value}({playside})')
            if len(tablekeys) >= 2:
                report.error(f'Duplicate key: {value}({playside})')
        
        keys1p = [*keyresult[value]['1P'].keys()]
        keys2p = [*keyresult[value]['2P'].keys()]
        if len(keys1p) == 1 and len(keys2p) == 1:
            if keys1p[0] != keys2p[0]:
                report_keycompare.append(f'Different key {value}')
    
    optionkeys_report_filepath = join(report_basedir_option, 'keys.txt')
    with open(optionkeys_report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(report_keys))
    
    keycompare_report_filepath = join(report_basedir_option, 'keycompare.txt')
    with open(keycompare_report_filepath, 'w', encoding='UTF-8') as f:
        f.write('\n'.join(report_keycompare))
    
    report.report()

    return {'useoption': useoptioncount, 'option': table}

def learning_cleartype(details):
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

def learning_djlevel(details):
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

def learning_numberbest(details):
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

def learning_numbercurrent(details):
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

def learning_not_new(details):
    report = Report('notnew')

    trimareas = {}
    for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
        trimareas[key] = details_define[key]['new']

    learning_targets = {}
    evaluate_targets = {}
    for key, target in details.items():
        for k in ['clear_type', 'dj_level', 'score', 'miss_count']:
            if not f'{k}_new' in target.label.keys() or target.label[f'{k}_new'] is True:
                continue

            trimmed = target.np_value[trimareas[k]]
            learning_targets[f'{key}_{k}.png'] = trimmed

        evaluate_targets[key] = target
    
    report.append_log(f'source count: {len(learning_targets)}')

    result = learning(learning_targets, report)
    if result is None:
        report.report()
        return

    for key, target in evaluate_targets.items():
        for k in ['clear_type', 'dj_level', 'score', 'miss_count']:
            is_new = f'{k}_new' in target.label.keys() and target.label[f'{k}_new']
            trimmed = target.np_value[trimareas[k]]
            recoged = np.all((result==0)|(trimmed==result))
            if (recoged and not is_new) or (not recoged and is_new):
                report.through()
            else:
                report.saveimage_errorvalue(trimmed, f'{key}_{k}.png')
                report.error(f'Mismatch {k}_new {is_new} {recoged} {key}')

    report.report()

    return result

def learning_graphtarget(details):
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

    details: dict[str, Details] = load_details(labels)
    
    if not exists(report_basedir_option):
        mkdir(report_basedir_option)

    table_graphtype = learning_graphtype(details)
    table_option = learning_option(details)
    table_clear_type = learning_cleartype(details)
    table_dj_level = learning_djlevel(details)
    table_number_best = learning_numberbest(details)
    table_number_current = learning_numbercurrent(details)
    mask_not_new = learning_not_new(details)
    table_graphtarget = learning_graphtarget(details)
 
    filename = f'details{define.details_recognition_version}.res'

    data = {
        'define': details_define,
        'graphtype': table_graphtype,
        'option': table_option,
        'clear_type': table_clear_type,
        'dj_level': table_dj_level,
        'number_best': table_number_best,
        'number_current': table_number_current,
        'not_new': mask_not_new,
        'graphtarget': table_graphtarget
    }
    
    save_resource_serialized(filename, data, True)
