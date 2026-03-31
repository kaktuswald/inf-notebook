import json
from sys import exit
from os.path import join,isfile

from PIL import Image
import numpy as np

from define import define
from data_collection import collection_basepath
from resources_generate import Report,save_resource_serialized,registries_dirname
from resources_learning import learning_multivalue,learning_multivaluemask,learning

images_resultothers_basepath = join(collection_basepath, 'resultothers')
label_filepath = join(collection_basepath, 'label_resultothers.json')

recognition_define_filename = 'define_recognition_resultothers.json'
recognition_define_filepath = join(registries_dirname, recognition_define_filename)

class ImageValues():
    def __init__(self, np_value, label):
        self.np_value = np_value
        self.label = label

def load_images(labels):
    keys = [key for key in labels.keys()]

    imagevaleus = {}
    for filename in keys:
        if 'ignore' in labels[filename].keys() and labels[filename]['ignore']:
            continue

        filepath = join(images_resultothers_basepath, filename)
        if not isfile(filepath):
            continue

        np_value = np.array(Image.open(filepath), dtype=np.uint8)
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

def learning_tab():
    report_tab = Report('resultothers_tab')

    define_target = resultothers_define['tab']

    trim = (
        slice(define_target['trim'][0][0], define_target['trim'][0][1]),
        slice(define_target['trim'][1][0], define_target['trim'][1][1]),
        define_target['trim'][2]
    )

    learning_targets = {}
    evaluate_targets = {}
    for key, target in imagevalues.items():
        if not 'tab' in target.label.keys() or target.label['tab'] == '':
            continue
        
        value = target.label['tab']
        trimmed = target.np_value[trim]
        if not value in learning_targets.keys():
            learning_targets[value] = {}
        learning_targets[value][key] = trimmed

        evaluate_targets[key] = target
    
    report_tab.append_log(f'Source count: {len(learning_targets)}')

    table = learning_multivalue(learning_targets, report_tab)
    if table is None:
        report_tab.report_tab()
        return

    for key, target in evaluate_targets.items():
        trimmed = target.np_value[trim]
        tablekey = trimmed.tobytes().hex()

        result = None
        if tablekey in table.keys():
            result = table[tablekey]
        
        if result == target.label['tab']:
            report_tab.through()
        else:
            report_tab.saveimage_errorvalue(trimmed, key)
            report_tab.error(f'Mismatch {result} {key}')

    resource['tab'] = {
        'trim': trim,
        'table': table
    }

    report_tab.report()

    if not report_tab.count_error:
        report.through()
    else:
        report.error('Error Tab')

def learning_ranknumbers():
    report_ranknumbers = Report('resultothers_ranknumbers')

    trims = {}
    for labelkey in ['rankbefore', 'ranknow']:
        define_target = resultothers_define[labelkey]

        trims[labelkey] = (
            slice(
                define_target['trim'][0][0],
                define_target['trim'][0][1],
                define_target['trim'][0][2],
            ),
            slice(
                define_target['trim'][1][0],
                define_target['trim'][1][1],
                define_target['trim'][1][2],
            ),
            define_target['trim'][2],
        )
    
    maskvalue = define_target['maskvalue']

    learning_targets = {}
    evaluate_targets = {}
    for key, target in imagevalues.items():
        has_rankbefore = None
        has_ranknow = None

        if 'rankbefore' in target.label.keys() and target.label['rankbefore'] != '':
            value = target.label['rankbefore']
            trimmed = target.np_value[trims['rankbefore']]
            if not value in learning_targets.keys():
                learning_targets[value] = {}
            learning_targets[value][key] = trimmed
            has_rankbefore = True

        if 'ranknow' in target.label.keys() and target.label['ranknow'] != '':
            value = target.label['ranknow']
            trimmed = target.np_value[trims['ranknow']]
            if not value in learning_targets.keys():
                learning_targets[value] = {}
            learning_targets[value][key] = trimmed
            has_ranknow = True

        if has_rankbefore and has_ranknow:
            evaluate_targets[key] = target
    
    report_ranknumbers.append_log(f'Source count: {len(learning_targets)}')

    table = learning_multivaluemask(learning_targets, report_ranknumbers, maskvalue)
    if table is None:
        report_ranknumbers.report_ranknumbers()
        return

    for key, target in evaluate_targets.items():
        for labelkey in ['rankbefore', 'ranknow']:
            trimmed = target.np_value[trims[labelkey]]
            bins = np.where(trimmed.flatten()==maskvalue, 1, 0)
            hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
            tablekey = ''.join([format(v, '0x') for v in hexs])

            result = None
            if tablekey in table.keys():
                result = table[tablekey]
            
            if result == target.label[labelkey]:
                report_ranknumbers.through()
            else:
                report_ranknumbers.saveimage_errorvalue(trimmed, key)
                report_ranknumbers.error(f'Mismatch {labelkey} {result} {key}')

    for labelkey in ['rankbefore', 'ranknow']:
        resource[labelkey] = {
            'trim': trims[labelkey],
            'maskvalue': maskvalue,
            'table': table
        }

    report_ranknumbers.report()

    if not report_ranknumbers.count_error:
        report.through()
    else:
        report.error('Error ranknumbers')

def learning_rankposition():
    report_rankposition = Report('resultothers_rankposition')

    define_target = resultothers_define['rankposition']

    trim = (
        slice(
            define_target['trim'][0][0],
            define_target['trim'][0][1],
            define_target['trim'][0][2],
        ),
        slice(
            define_target['trim'][1][0],
            define_target['trim'][1][1],
        ),
        define_target['trim'][2],
    )
    maskvalue = define_target['maskvalue']

    learning_targets = {}
    evaluate_targets = {}
    for key, target in imagevalues.items():
        if not 'rankposition' in target.label.keys() or target.label['rankposition'] == '':
            continue
        
        value = int(target.label['rankposition'])
        trimmed = target.np_value[trim]
        if not value in learning_targets.keys():
            learning_targets[value] = {}
        learning_targets[value][key] = trimmed

        evaluate_targets[key] = target
    
    report_rankposition.append_log(f'Source count: {len(learning_targets)}')

    table = learning_multivaluemask(learning_targets, report_rankposition, maskvalue)
    if table is None:
        report_rankposition.report_rankposition()
        return

    for key, target in evaluate_targets.items():
        trimmed = target.np_value[trim]
        bins = np.where(trimmed.flatten()==maskvalue, 1, 0)
        hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
        tablekey = ''.join([format(v, '0x') for v in hexs])

        result = None
        if tablekey in table.keys():
            result = table[tablekey]
        
        if result == int(target.label['rankposition']):
            report_rankposition.through()
        else:
            report_rankposition.saveimage_errorvalue(trimmed, key)
            report_rankposition.error(f'Mismatch {result} {key}')

    resource['rankposition'] = {
        'trim': trim,
        'maskvalue': maskvalue,
        'table': table,
    }

    report_rankposition.report()

    if not report_rankposition.count_error:
        report.through()
    else:
        report.error('Error rankposition')

def learning_notesradar_attribute():
    report_notesradar_attribute = Report('resultothers_notesradar_attribute')

    define_target = resultothers_define['notesradar_attribute']

    trim = (
        slice(
            define_target['trim'][0][0],
            define_target['trim'][0][1],
        ),
        slice(
            define_target['trim'][1][0],
            define_target['trim'][1][1],
        ),
        define_target['trim'][2],
    )
    maskvalue = define_target['maskvalue']

    learning_targets = {}
    evaluate_targets = {}
    for key, target in imagevalues.items():
        if not 'radarattribute' in target.label.keys() or target.label['radarattribute'] == '':
            continue
        
        value = target.label['radarattribute']
        trimmed = target.np_value[trim]
        if not value in learning_targets.keys():
            learning_targets[value] = {}
        learning_targets[value][key] = trimmed

        evaluate_targets[key] = target
    
    report_notesradar_attribute.append_log(f'Source count: {len(learning_targets)}')

    table = learning_multivaluemask(learning_targets, report_notesradar_attribute, maskvalue)
    if table is None:
        report_notesradar_attribute.report()
        return

    for key, target in evaluate_targets.items():
        trimmed = target.np_value[trim]
        bins = np.where(trimmed.flatten()==maskvalue, 1, 0)
        hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
        tablekey = ''.join([format(v, '0x') for v in hexs])

        result = None
        if tablekey in table.keys():
            result = table[tablekey]
        
        if result == target.label['radarattribute']:
            report_notesradar_attribute.through()
        else:
            report_notesradar_attribute.saveimage_errorvalue(trimmed, key)
            report_notesradar_attribute.error(f'Mismatch {result} {key}')

    resource['notesradar_attribute'] = {
        'trim': trim,
        'maskvalue': maskvalue,
        'table': table,
    }

    report_notesradar_attribute.report()

    if not report_notesradar_attribute.count_error:
        report.through()
    else:
        report.error('Error notesradar attribute')

def learning_notesradar_chartvaluenumber():
    report_notesradar_chartvaluenumber = Report('resultothers_notesradar_chartvaluenumber')

    define_target = resultothers_define['notesradar_chartvalue']

    trim = (
        slice(
            define_target['trim'][0][0],
            define_target['trim'][0][1],
        ),
        slice(
            define_target['trim'][1][0],
            define_target['trim'][1][1],
        ),
        define_target['trim'][2],
    )
    
    onedigitwidth = define_target['onedigitwidth']
    leftpositions = define_target['leftpositions']
    maskvalue = define_target['maskvalue']

    learning_targets = {}
    for i in range(10):
        learning_targets[i] = {}

    evaluate_targets = {}
    for key, target in imagevalues.items():
        if not 'radarchartvalue' in target.label.keys() or target.label['radarchartvalue'] == '':
            continue

        value = int(target.label['radarchartvalue'].replace('.', ''))
        trimmed1 = target.np_value[trim]

        for i in range(len(leftpositions)):
            if value < 10 ** (len(leftpositions) - i):
                continue

            onedigitvalue = value // (10 ** (len(leftpositions) - 1 - i)) % 10
            trimmed2 = trimmed1[:, leftpositions[i]:leftpositions[i]+onedigitwidth]

            learning_targets[onedigitvalue][f'{key}_{i}_{onedigitvalue}'] = trimmed2

        evaluate_targets[key] = target
    
    report_notesradar_chartvaluenumber.append_log(f'Source count: {len(learning_targets)}')

    table = learning_multivaluemask(learning_targets, report_notesradar_chartvaluenumber, maskvalue)
    if table is None:
        report.error('Error notesradar chartvaluenumber')
        report_notesradar_chartvaluenumber.report()
        return

    if len(table) != len(learning_targets):
        report_notesradar_chartvaluenumber.error('Incomplete keys')

    for key, target in evaluate_targets.items():
        trimmed1 = target.np_value[trim]

        value = None
        for i in range(len(leftpositions)):
            trimmed2 = trimmed1[:, leftpositions[i]:leftpositions[i]+onedigitwidth]
            bins = np.where(trimmed2.flatten()==maskvalue, 1, 0)
            hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
            tablekey = ''.join([format(v, '0x') for v in hexs])
            if tablekey in table.keys():
                if value is None:
                    value = 0
                value += table[tablekey] * (10 ** (len(leftpositions) - i - 1))
        strvalue = f'{value/100:.2f}' if value is not None else None

        if strvalue == target.label['radarchartvalue']:
            report_notesradar_chartvaluenumber.through()
        else:
            report_notesradar_chartvaluenumber.saveimage_errorvalue(trimmed1, key)
            report_notesradar_chartvaluenumber.error(f'Mismatch {strvalue} {target.label['radarchartvalue']} {key}')

    resource['notesradar_chartvalue'] = {
        'trim': trim,
        'onedigitwidth': onedigitwidth,
        'leftpositions': leftpositions,
        'maskvalue': maskvalue,
        'table': table,
    }

    report_notesradar_chartvaluenumber.report()

    if not report_notesradar_chartvaluenumber.count_error:
        report.through()
    else:
        report.error('Error notesradar chartvaluenumber')

def learning_notesradar_valuenumber():
    report_notesradar_valuenumber = Report('resultothers_notesradar_valuenumber')

    define_target = resultothers_define['notesradar_value']

    trim = (
        slice(
            define_target['trim'][0][0],
            define_target['trim'][0][1],
        ),
        slice(
            define_target['trim'][1][0],
            define_target['trim'][1][1],
        ),
        define_target['trim'][2],
    )
    
    typekeys = ['normal', 'updated']

    onedigitwidth = define_target['onedigitwidth']
    leftpositions = define_target['leftpositions']

    maskvalues = {}
    for typekey in typekeys:
        maskvalues[typekey] = define_target[f'maskvalue{typekey}']

    learning_targets = {}
    for typekey in typekeys:
        learning_targets[typekey] = {}
        for i in range(10):
            learning_targets[typekey][i] = {}

    evaluate_targets = {}
    for key, target in imagevalues.items():
        if not 'radarvalue' in target.label.keys() or target.label['radarvalue'] == '':
            continue
        if not 'radarupdated' in target.label.keys() or target.label['radarupdated'] == None:
            continue
        
        typekey = 'normal' if not target.label['radarupdated'] else 'updated'
        value = int(target.label['radarvalue'].replace('.', ''))
        trimmed1 = target.np_value[trim]

        for i in range(len(leftpositions)):
            if value < 10 ** (len(leftpositions) - i):
                continue

            onedigitvalue = value // (10 ** (len(leftpositions) - 1 - i)) % 10
            trimmed2 = trimmed1[:, leftpositions[i]:leftpositions[i]+onedigitwidth]

            learning_targets[typekey][onedigitvalue][f'{key}_{typekey}_{i}_{onedigitvalue}'] = trimmed2

        evaluate_targets[key] = target
    
    report_notesradar_valuenumber.append_log(f'Source count: {len(learning_targets)}')

    table = {
        'normal': learning_multivaluemask(
            learning_targets['normal'],
            report_notesradar_valuenumber,
            maskvalues['normal'],
        ),
        'updated': learning_multivaluemask(
            learning_targets['updated'],
            report_notesradar_valuenumber,
            maskvalues['updated'],
        ),
    }

    if table['normal'] is None or table['updated'] is None:
        report.error('Error notesradar valuenumber')
        report_notesradar_valuenumber.report()
        return

    for typekey in typekeys:
        if len(table[typekey]) != len(learning_targets[typekey]):
            report_notesradar_valuenumber.error(f'Incomplete keys {typekey}')

    for key, target in evaluate_targets.items():
        trimmed1 = target.np_value[trim]

        is_updated = False
        for typekey in ['normal', 'updated']:
            value = None
            for i in range(len(leftpositions)-1, -1, -1):
                trimmed2 = trimmed1[:, leftpositions[i]:leftpositions[i]+onedigitwidth]
                bins = np.where(trimmed2.flatten()==maskvalues[typekey], 1, 0)
                hexs=bins[::4]*8+bins[1::4]*4+bins[2::4]*2+bins[3::4]
                tablekey = ''.join([format(v, '0x') for v in hexs])

                if value is None and not tablekey in table[typekey].keys():
                    break

                if tablekey in table[typekey].keys():
                    if value is None:
                        value = 0
                    value += table[typekey][tablekey] * (10 ** (len(leftpositions) - i - 1))
            
            if value is not None:
                if typekey == 'updated':
                    is_updated = True
                break

        strvalue = f'{value/100:.2f}' if value is not None else None

        if strvalue == target.label['radarvalue']:
            report_notesradar_valuenumber.through()
        else:
            report_notesradar_valuenumber.saveimage_errorvalue(trimmed1, key)
            report_notesradar_valuenumber.error(f'Mismatch {strvalue} {target.label['radarvalue']} {key}')

    resource['notesradar_value'] = {
        'trim': trim,
        'onedigitwidth': onedigitwidth,
        'leftpositions': leftpositions,
        'table': table,
        'maskvalues': maskvalues,
    }

    report_notesradar_valuenumber.report()

    if not report_notesradar_valuenumber.count_error:
        report.through()
    else:
        report.error('Error notesradar valuenumber')

if __name__ == '__main__':
    try:
        with open(label_filepath) as f:
            labels = json.load(f)
    except Exception:
        print(f"{label_filepath}を読み込めませんでした。")
        exit()

    resultothers_define = load_define()
    if resultothers_define is None:
        exit()

    imagevalues = load_images(labels)
    
    resource = {}

    report = Report('resultothers')

    learning_tab()
    learning_ranknumbers()
    learning_rankposition()
    learning_notesradar_attribute()
    learning_notesradar_chartvaluenumber()
    learning_notesradar_valuenumber()

    filename = f'resultothers{define.resultothers_recognition_version}.res'
    save_resource_serialized(filename, resource, True)

    report.report()

