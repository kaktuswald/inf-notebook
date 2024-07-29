import numpy as np
from sys import argv

from define import define
from resources_generate import Report,load_raws,save_resource_numpy
from resources_larning import larning

resourcenames = {
    'rival': 'rival',
    'play_side': 'play_side',
    'dead': 'dead'
}

def larning_rival(raws):
    resourcename = resourcenames['rival']

    report = Report(resourcename)

    trimarea = define.areas_np['rival']

    larning_targets = {}
    evaluate_targets = {}
    for filename, raw in raws.items():
        if not 'screen' in raw.label.keys() or raw.label['screen'] != 'result':
            continue
        if not 'rival' in raw.label.keys():
            continue

        if raw.label['rival']:
            trimmed = raw.np_value[trimarea]
            larning_targets[filename] = trimmed
        evaluate_targets[filename] = raw
    
    report.append_log(f'source count: {len(larning_targets)}')

    result = larning(larning_targets, report)
    if result is None:
        report.report()
        return

    for filename, raw in evaluate_targets.items():
        is_rival = raw.label['rival']
        trimmed = raw.np_value[trimarea]
        recoged = np.all((result==0)|(trimmed==result))
        if (recoged and is_rival) or (not recoged and not is_rival):
            report.through()
        else:
            report.saveimage_errorvalue(trimmed, filename)
            report.error(f'Mismatch {is_rival} {filename}')

    save_resource_numpy(resourcename, result)

    report.report()

def larning_playside(raws):
    resourcename = resourcenames['play_side']

    report = Report(resourcename)

    trimareas = define.areas_np['play_side']

    larning_targets = {}
    evaluate_targets = {}
    for filename, raw in raws.items():
        if not 'screen' in raw.label.keys() or raw.label['screen'] != 'result':
            continue
        if not 'is_savable' in raw.label.keys() or raw.label['is_savable']:
            continue
        if not 'play_side' in raw.label.keys() or not raw.label['play_side'] in define.value_list['play_sides']:
            continue

        play_side = raw.label['play_side']
        trimmed = raw.np_value[trimareas[play_side]]
        larning_targets[filename] = trimmed

        evaluate_targets[filename] = raw
    
    report.append_log(f'source count: {len(larning_targets)}')

    result = larning(larning_targets, report)
    if result is None:
        report.report()
        return

    for filename, raw in evaluate_targets.items():
        recoged = None
        for key, area in trimareas.items():
            if np.all((result==0)|(raw.np_value[area]==result)):
                recoged = key
        play_side = raw.label['play_side']
        if recoged == play_side:
            report.through()
        else:
            report.saveimage_errorvalue(trimmed, filename)
            report.error(f'Mismatch {recoged} {filename}')

    save_resource_numpy(resourcename, result)

    report.report()

def larning_dead(raws):
    resourcename = resourcenames['dead']

    report = Report(resourcename)

    trimareas = define.areas_np['dead']

    larning_targets = {}
    evaluate_targets = {}
    for filename, raw in raws.items():
        if not 'screen' in raw.label.keys() or raw.label['screen'] != 'result':
            continue
        if not 'dead' in raw.label.keys():
            continue
        if not 'play_side' in raw.label.keys() or not raw.label['play_side'] in define.value_list['play_sides']:
            continue

        if raw.label['dead']:
            play_side = raw.label['play_side']
            trimmed = raw.np_value[trimareas[play_side]]
            larning_targets[filename] = trimmed
        evaluate_targets[filename] = raw
    
    report.append_log(f'source count: {len(larning_targets)}')

    result = larning(larning_targets, report)
    if result is None:
        report.report()
        return

    for filename, raw in evaluate_targets.items():
        is_dead = raw.label['dead']
        play_side = raw.label['play_side']
        trimmed = raw.np_value[trimareas[play_side]]
        recoged = np.all((result==0)|(trimmed==result))
        if (recoged and is_dead) or (not recoged and not is_dead):
            report.through()
        else:
            report.saveimage_errorvalue(trimmed, filename)
            report.error(f'Mismatch {is_dead} {filename}')

    save_resource_numpy(resourcename, result)

    report.report()

if __name__ == '__main__':
    if len(argv) == 1:
        print('please argment.')
        exit()

    raws = load_raws()

    if '-all' in argv or '-rival' in argv:
        larning_rival(raws)

    if '-all' in argv or '-playside' in argv:
        larning_playside(raws)

    if '-all' in argv or '-dead' in argv:
        larning_dead(raws)
