import numpy as np
from sys import argv

from define import define
from resources_generate import Report,load_raws,save_resource_serialized

error_file_output_count = 3

resourcenames = {
    'get_screen': 'get_screen.res',
    'is_savable': 'is_savable.res',
}

def generate_get_screen(raws):
    resourcename = resourcenames['get_screen']

    report = Report(resourcename)
    
    left = define.get_screen_area['left']
    bottom = define.height - define.get_screen_area['top']
    right = left + define.get_screen_area['width']
    top = bottom - define.get_screen_area['height']
    area = (slice(top, bottom), slice(left, right))

    table = {}
    for filename, raw in raws.items():
        if not 'screen' in raw.label.keys():
            continue

        screen = raw.label['screen']
        if not raw.label['screen'] in ['loading', 'result', 'music_select']:
            continue

        np_value_reverse = raw.np_value[::-1, :, ::-1]
        key_value = np_value_reverse[area]
        key = np.sum(key_value)

        if not screen in table.values():
            table[key] = screen
            report.saveimage_value(key_value, f'{screen}-{filename}')
            report.append_log(f'{screen}: {key}')
        
        if key in table.keys() and table[key] == screen:
            report.through()
        else:
            report.saveimage_errorvalue(key_value, filename)
            if key in table.keys():
                report.error(f'Mismatch {key}: {screen} and {table[key]} of {filename}')
            else:
                report.error(f'Not found {key}: {screen} of {filename}')

    save_resource_serialized(resourcename, table)

    report.report()

def generate_is_savable(raws):
    resourcename = resourcenames['is_savable']

    report = Report(resourcename)

    raw_targets = {}
    for filename, raw in raws.items():
        if not 'screen' in raw.label.keys() or raw.label['screen'] != 'result':
            continue
        if not 'cutin_mission' in raw.label.keys() or raw.label['cutin_mission']:
            continue
        if not 'cutin_bit' in raw.label.keys() or raw.label['cutin_bit']:
            continue

        background_key = raw.np_value[define.result_check['background_key_position']]
        if not background_key in raw_targets.keys():
            raw_targets[background_key] = {}
        raw_targets[background_key][filename] = raw
    
    if len(raw_targets) == define.result_check['background_count']:
        report.log(f'background count: {len(raw_targets)}')
        sorted_keys = sorted([*raw_targets.keys()])
        for background_key in sorted_keys:
            report.log(f'"{background_key}" raw count: {len(raw_targets[background_key])}')
    else:
        report.log(f'Wrong background count: {len(raw_targets)}')

        report.report()
        return
    
    table = {}
    for background_key, targets in raw_targets.items():
        table[background_key] = {}
        for area_key, area in define.result_check['areas'].items():
            filename, raw = [*targets.items()][0]
            value = raw.np_value[area]
            table[background_key][area_key] = value
            report.saveimage_value(value, f'{background_key}-{area_key}-{filename}')

        for filename, raw in targets.items():
            for area_key, area in define.result_check['areas'].items():
                value = raw.np_value[area]
                if np.array_equal(value, table[background_key][area_key]):
                    report.through()
                else:
                    report.saveimage_errorvalue(value, filename)
                    report.error(f'Mismatch {background_key} {area_key} {filename}')

    save_resource_serialized(resourcename, table)

    report.report()

if __name__ == '__main__':
    if len(argv) == 1:
        print('please argment.')
        exit()

    raws = load_raws()

    if '-all' in argv or '-get_screen' in argv:
        generate_get_screen(raws)

    if '-all' in argv or '-is_savable' in argv:
        generate_is_savable(raws)
    