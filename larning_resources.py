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
    'dead': 'dead'
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

        raws[filename] = RawData(np.array(Image.open(filepath).convert('RGB')), label)
    
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

def output_report(report_dirpath, report, output_linecount):
    report_filepath = join(report_dirpath, 'report.txt')
    with open(report_filepath, 'w') as f:
        f.write('\n'.join(report))
    
    for line in report[:output_linecount]:
        print(line)

def larning(targets, report_dirpath, report):
    if len(raws) == 0:
        report.append('count: 0')
        return None

    patterns = []
    listeds = []
    for filename, np_value in targets.items():
        listed = np_value.tolist()
        if not listed in listeds:
            patterns.append(np_value)
            listeds.append(listed)
            filepath = join(report_dirpath, f"pattern{len(patterns):02}-{filename}")
            Image.fromarray(np_value).save(filepath)
    
    report.append(f'pattern count: {len(patterns)}')

    result = np.copy(patterns[0])
    for target in patterns[1:]:
        result = np.where(result|result==target, result, 0)

    if np.sum(result) == 0:
        report.append('Result equal 0')
        return None

    return result

def larning_dead(raws):
    resource_name = resourcenames['dead']
    report_output_linecount = 20

    report_dirpath = get_report_dir(resource_name)
    report = []
    file_count = 0

    trimareas = define.areas_np['dead']

    larning_targets = {}
    evaluate_targets = {}
    for filename, raw in raws.items():
        if not 'screen' in raw.label.keys() or raw.label['screen'] != 'result':
            continue
        if not 'dead' in raw.label.keys():
            continue
        if not 'cutin_bit' in raw.label.keys() or raw.label['cutin_bit']:
            continue
        if not 'play_side' in raw.label.keys() or not raw.label['play_side'] in define.value_list['play_sides']:
            continue

        if raw.label['dead']:
            play_side = raw.label['play_side']
            trimmed = raw.np_value[trimareas[play_side]]
            larning_targets[filename] = trimmed
        evaluate_targets[filename] = raw
    
    report.append(f'source count: {len(larning_targets)}')

    result = larning(larning_targets, report_dirpath, report)
    if result is None:
        output_report(report_dirpath, report, report_output_linecount)
        return

    through_count = 0
    error_count = 0
    for filename, raw in evaluate_targets.items():
        is_dead = raw.label['dead']
        play_side = raw.label['play_side']
        trimmed = raw.np_value[trimareas[play_side]]
        recoged = np.all((result==0)|(trimmed==result))
        if (recoged and is_dead) or (not recoged and not is_dead):
            through_count += 1
        else:
            if file_count < file_output_count:
                image = Image.fromarray(trimmed)
                image.save(join(report_dirpath, filename))
                file_count += 1
            report.append(f'Mismatch {is_dead} {filename}')
            error_count += 1

    if error_count == 0:
        report.append('Complete')
        report.append(f'Through count: {through_count}')
    else:
        report.append(f'Error count: {error_count}')
        report.append('\n'.join(report))

    create_resource_directory()
    filepath = join(resources_dirname, resource_name)
    np.save(filepath, result)

    output_report(report_dirpath, report, report_output_linecount)

if __name__ == '__main__':
    if len(argv) == 1:
        print('please argment.')
        exit()

    raws = load_raws()

    if '-all' in argv or '-dead' in argv:
        larning_dead(raws)
    