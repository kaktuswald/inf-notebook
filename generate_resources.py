import numpy as np
import pickle
from os import mkdir,remove
from os.path import join,exists,isfile
from PIL import Image
from glob import glob
from sys import argv

from define import define
from raw_image import raws_basepath
from larning import RawLabel,create_resource_directory
from resources import resources_dirname

file_output_count = 3

report_dirname = 'report'

resourcenames = {
    'screen': 'screen.res',
    'is_savable': 'is_savable.res',
}

class RawData():
    def __init__(self, np_value, label):
        self.np_value = np_value
        self.label = label

def load_raws():
    labels = RawLabel()

    filenames = [*labels.all()]

    raws = {}
    for filename in filenames:
        filepath = join(raws_basepath, filename)
        if not isfile(filepath):
            continue

        label = labels.get(filename)
        if not 'screen' in label.keys():
            continue

        raws[filename] = RawData(np.array(Image.open(filepath).convert('RGB'))[::-1, :, ::-1], label)
    
    print(f"raw count: {len(raws)}")

    return raws

def get_report_dir(resource_name):
    if not exists(report_dirname):
        mkdir(report_dirname)
    
    report_dirpath = join(report_dirname, resource_name)
    for filepath in glob(join(report_dirpath, '*')):
        remove(filepath)
    if not exists(report_dirpath):
        mkdir(report_dirpath)
    
    return report_dirpath

def generate_screen(raws):
    resource_name = resourcenames['screen']
    report_output_linecount = 10

    report_dirpath = get_report_dir(resource_name)
    report = []
    file_count = 0
    
    table = {}
    for filename, raw in raws.items():
        if not 'screen' in raw.label.keys():
            continue

        screen = raw.label['screen']

        if not screen in define.screen_names:
            continue

        if not screen in table.values():
            key_value = raw.np_value[define.screen_area]
            key = ''.join([format(v, '0x') for v in key_value])
            table[key] = screen
            image = Image.fromarray(key_value)
            image.save(join(report_dirpath, f'{screen}-{filename}'))
            report.append(f'{screen}: {key}')

    through_count = 0
    error_count = 0
    for filename, raw in raws.items():
        if 'screen' in raw.label.keys():
            screen = raw.label['screen']
        else:
            screen = None

        key_value = raw.np_value[define.screen_area]
        key = ''.join([format(v, '0x') for v in key_value])
        has_key = key in table
        is_target_screen = screen in define.screen_names
        if has_key == is_target_screen:
            through_count += 1
        else:
            if file_count < file_output_count:
                image = Image.fromarray(key_value)
                image.save(join(report_dirpath, filename))
                file_count += 1
            if has_key:
                report.append(f'{screen} was recognized as {table[key]} from {filename}...{key}')
            else:
                report.append(f'Not recognized {screen} from {filename}...{key}')
            error_count += 1

    if error_count == 0:
        report.append('Complete')
        report.append(f'Through count: {through_count}')
    else:
        report.append(f'Error count: {error_count}')
        report.append('\n'.join(report))

    create_resource_directory()
    filepath = join(resources_dirname, resource_name)
    with open(filepath, 'wb') as f:
        pickle.dump(table, f)

    report_filepath = join(report_dirpath, 'report.txt')
    with open(report_filepath, 'w') as f:
        f.write('\n'.join(report))
    
    for line in report[:report_output_linecount]:
        print(line)

def generate_is_savable(raws):
    resource_name = resourcenames['is_savable']
    report_output_linecount = 20

    report_dirpath = get_report_dir(resource_name)
    report = []
    file_count = 0

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
        report.append(f'background count: {len(raw_targets)}')
        sorted_keys = sorted([*raw_targets.keys()])
        for background_key in sorted_keys:
            report.append(f'"{background_key}" raw count: {len(raw_targets[background_key])}')
    else:
        report.append(f'Wrong background count: {len(raw_targets)}')

        for line in report[:report_output_linecount]:
            print(line)

        exit()
    
    table = {}
    through_count = 0
    error_count = 0
    for background_key, targets in raw_targets.items():
        table[background_key] = {}
        for area_key, area in define.result_check['areas'].items():
            filename, raw = [*targets.items()][0]
            value = raw.np_value[area]
            table[background_key][area_key] = value
            image = Image.fromarray(value)
            image.save(join(report_dirpath, f'{background_key}-{area_key}-{filename}'))

        for filename, raw in targets.items():
            for area_key, area in define.result_check['areas'].items():
                value = raw.np_value[area]
                if np.array_equal(value, table[background_key][area_key]):
                    through_count += 1
                else:
                    if file_count < file_output_count:
                        image = Image.fromarray(value)
                        image.save(join(report_dirpath, filename))
                        file_count += 1
                    report.append(f'Mismatch {background_key} {area_key} {filename}')
                    error_count += 1

    if error_count == 0:
        report.append('Complete')
        report.append(f'Through count: {through_count}')
    else:
        report.append(f'Error count: {error_count}')
        report.append('\n'.join(report))

    create_resource_directory()
    filepath = join(resources_dirname, resource_name)
    with open(filepath, 'wb') as f:
        pickle.dump(table, f)

    report_filepath = join(report_dirpath, 'report.txt')
    with open(report_filepath, 'w') as f:
        f.write('\n'.join(report))

    for line in report[:report_output_linecount]:
        print(line)

if __name__ == '__main__':
    if len(argv) == 1:
        print('please argment.')
        exit()

    raws = load_raws()

    if '-all' in argv or '-screen' in argv:
        generate_screen(raws)

    if '-all' in argv or '-is_savable' in argv:
        generate_is_savable(raws)
    