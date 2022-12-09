from PIL import Image
import os
import numpy as np
import shutil
import glob
from logging import getLogger

logger_child_name = 'larning'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded larning.py')

from resources import areas,create_resource_directory,create_masks_directory,save_mask
from define import value_list,option_widths
from labels import larning_source_label

larning_sources_basepath = 'larning_sources'

larningbase_direpath = 'larning'
mask_images_dirpath = os.path.join(larningbase_direpath, 'mask_images')

def create_larning_source_directory():
    if not os.path.exists(larning_sources_basepath):
        os.mkdir(larning_sources_basepath)

def save_larning_source(screen):
    filepath = os.path.join(larning_sources_basepath, screen.filename)
    if not os.path.exists(filepath):
        screen.original.save(filepath)

def get_larning_sources():
    labels = larning_source_label()
    ret = []
    for filepath in glob.glob(os.path.join(larning_sources_basepath, '*.bmp')):
        filename = os.path.basename(filepath)
        if filename in labels.all():
            ret.append({
                'filepath': filepath,
                'label': labels.get(filename),
            })
    return ret

def larning(key, targets):
    if len(targets) == 0:
        return

    pattern_count = 0
    patterns = []

    larning_dirpath = os.path.join(larningbase_direpath, key)
    if os.path.exists(larning_dirpath):
        try:
            shutil.rmtree(larning_dirpath)
        except Exception as ex:
            print(ex)

    if not os.path.exists(larning_dirpath):
        os.mkdir(larning_dirpath)

    for target in targets.items():
        if not target[1] in patterns:
            patterns.append(target[1])
            pattern_count += 1
            filepath = os.path.join(larning_dirpath, f"{pattern_count}-{target[0]}")
            target[1].save(filepath)
    
    np_targets = [np.array(target) for target in targets.values()]

    mask = np.copy(np_targets[0])
    for target in np_targets[1:]:
        mask = np.where(mask|mask==target, mask, 0)

    save_mask(key, mask)

    mask_image = Image.fromarray(mask)

    larning_filepath = os.path.join(larning_dirpath, f"{key}.bmp")
    mask_image.save(larning_filepath)

    mask_image_filepath = os.path.join(mask_images_dirpath, f"{key}.bmp")
    mask_image.save(mask_image_filepath)

    print(f"[{key}]source count: {len(targets)} / pattern count: {len(patterns)}")

    return mask

def larning_values(key, value_list):
    targets = {}
    for value_name in value_list:
        targets[value_name] = {}

    for filename, image in images.items():
        label = labels.get(filename)
        if key in label.keys() and label[key] in value_list:
            targets[label[key]][filename] = image.crop(areas[key])

    for value_name in value_list:
        larning(value_name, targets[value_name])

def larning_find(key):
    targets = {}
    for filename, image in images.items():
        label = labels.get(filename)
        if key in label.keys() and label[key]:
            targets[filename] = image.crop(areas[key])

    larning(key, targets)

def is_result_ok(label):
    if not label['trigger']:
        return False
    
    if label['cutin_mission']:
        return False
    if label['cutin_bit']:
        return False
    
    if label['play_side'] == '':
        return False
    
    return True
    
def larning_level():
    targets = {}
    for difficulty in value_list['difficulties']:
        targets[difficulty] = {}
        for level in value_list['levels']:
            targets[difficulty][level] = {}

    for filename, image in images.items():
        label = labels.get(filename)
        if is_result_ok(label):
            difficulty = label['difficulty'] if 'difficulty' in label.keys() else ''
            level = label['level'] if 'level' in label.keys() else ''
            if difficulty != '' and level != '':
                targets[difficulty][level][filename] = image.crop(areas['level'])

    for difficulty in targets.keys():
        for level in targets[difficulty].keys():
            larning(f'{difficulty}-{level}', targets[difficulty][level])

def larning_by_side(key):
    targets = {}
    for filename, image in images.items():
        label = labels.get(filename)
        if is_result_ok(label) and key in label.keys() and label[key]:
            targets[filename] = image.crop(areas[label['play_side']][key])

    larning(key, targets)

def larning_values_by_side(key, value_list):
    targets = {}
    for value_name in value_list:
        targets[value_name] = {}
    
    for filename, image in images.items():
        label = labels.get(filename)
        if is_result_ok(label):
            if key in label.keys() and label[key] in value_list:
                targets[label[key]][filename] = image.crop(areas[label['play_side']][key])
    
    for value_name in value_list:
        larning(value_name, targets[value_name])

def larning_option():
    option_value_list = [
        *value_list['options_arrange'],
        *value_list['options_arrange_dp'],
        *value_list['options_arrange_sync'],
        *value_list['options_flip'],
        *value_list['options_assist'],
        'BATTLE',
        'H-RANDOM'
    ]

    targets = {}
    for value_name in option_value_list:
        targets[value_name] = {}
    
    for filename, image in images.items():
        label = labels.get(filename)

        if not 'play_mode' in label.keys() or label['play_mode'] == '':
            continue

        if not 'play_side' in label.keys() or label['play_side'] == '':
            continue

        play_side = label['play_side']

        if not 'use_option' in label.keys() or not label['use_option']:
            continue

        area = areas[play_side]['option'].copy()

        if 'option_battle' in label.keys() and label['option_battle']:
            targets['BATTLE'][filename] = image.crop(area)
            area[0] += option_widths['BATTLE'] + option_widths[',']
            area[2] += option_widths['BATTLE'] + option_widths[',']
        
        if 'option_arrange' in label.keys() and label['option_arrange'] != '':
            key = label['option_arrange']
            targets[key][filename] = image.crop(area)
            area[0] += option_widths[key] + option_widths[',']
            area[2] += option_widths[key] + option_widths[',']

        if 'option_arrange_dp' in label.keys() and label['option_arrange_dp'] != '/':
            left, right = label['option_arrange_dp'].split('/')
            targets[left][filename] = image.crop(area)
            area[0] += option_widths[left] + option_widths['/']
            area[2] += option_widths[left] + option_widths['/']
            targets[right][filename] = image.crop(area)
            area[0] += option_widths[right] + option_widths[',']
            area[2] += option_widths[right] + option_widths[',']

        if 'option_arrange_sync' in label.keys() and label['option_arrange_sync'] != '':
            key = label['option_arrange_sync']
            targets[key][filename] = image.crop(area)
            area[0] += option_widths[key] + option_widths[',']
            area[2] += option_widths[key] + option_widths[',']

        if 'option_h-random' in label.keys() and label['option_h-random']:
            targets['H-RANDOM'][filename] = image.crop(area)
            area[0] += option_widths['H-RANDOM'] + option_widths[',']
            area[2] += option_widths['H-RANDOM'] + option_widths[',']

        if 'option_flip' in label.keys() and label['option_flip'] != '':
            key = label['option_flip']
            targets[key][filename] = image.crop(area)
            area[0] += option_widths[key] + option_widths[',']
            area[2] += option_widths[key] + option_widths[',']

        if 'option_assist' in label.keys() and label['option_assist'] != '':
            key = label['option_assist']
            targets[key][filename] = image.crop(area)
            area[0] += option_widths[key] + option_widths[',']
            area[2] += option_widths[key] + option_widths[',']

    for value_name in option_value_list:
        larning(value_name, targets[value_name])

def larning_new():
    targets = {}
    for filename, image in images.items():
        label = labels.get(filename)
        if is_result_ok(label):
            for key in ['clear_type_new', 'dj_level_new', 'score_new', 'miss_count_new']:
                if key in label.keys() and not label[key]:
                    targets[f"{key}-{filename}"] = image.crop(areas[label['play_side']][key])

    larning('new', targets)

def larning_number():
    number_areas = {}
    for play_side in value_list['play_sides']:
        number_areas[play_side] = {}
        for type in ['score', 'miss_count']:
            number_areas[play_side][type] = []
            left, top, right, bottom = areas[play_side][type]
            width = right - left
            for i in range(4):
                number_areas[play_side][type].append([
                    int(left + width * i / 4),
                    top,
                    int(left + width * (i+1) / 4),
                    bottom
                ])

    targets = {
        '0': {},
        '1': {},
        '2': {},
        '3': {},
        '4': {},
        '5': {},
        '6': {},
        '7': {},
        '8': {},
        '9': {},
    }
    for filename, image in images.items():
        label = labels.get(filename)
        if is_result_ok(label):
            play_side = label['play_side']
            for key in ['score', 'miss_count']:
                if key in label.keys() and label[key].isdecimal():
                    score = int(label[key])
                    digit = 1
                    while int(score) > 0 or digit == 1:
                        number = str(int(score % 10))
                        targets[number][f"s{key}-{digit}-{filename}"] = image.crop(number_areas[play_side][key][4-digit])
                        score /= 10
                        digit += 1

    for number in targets.keys():
        if len(targets[number]) != 0:
            larning(number, targets[number])


if __name__ == '__main__':
    labels = larning_source_label()

    if not os.path.exists(larningbase_direpath):
        os.mkdir(larningbase_direpath)

    if not os.path.exists(mask_images_dirpath):
        os.mkdir(mask_images_dirpath)

    filenames = [*labels.all()]
    print(f"file count: {len(filenames)}")

    images = {}
    for filename in filenames:
        filepath = os.path.join('larning_sources', filename)
        if os.path.isfile(filepath):
            image = Image.open(filepath)
            images[filename] = image.convert('L')

    create_resource_directory()
    create_masks_directory()

    larning_values('starting', value_list['startings'])

    larning_find('trigger')
    larning_find('cutin_mission')
    larning_find('cutin_bit')
    larning_find('rival')

    larning_values('play_mode', value_list['play_modes'])
    larning_values('difficulty', value_list['difficulties'])
    larning_level()

    larning_by_side('play_side')
    larning_by_side('use_option')

    larning_option()

    larning_values_by_side('clear_type', value_list['clear_types'])
    larning_values_by_side('dj_level', value_list['dj_levels'])

    larning_new()

    larning_number()
