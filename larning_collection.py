from PIL import Image
import os
from sys import argv,exit
from logging import getLogger
import json

logger_child_name = 'larning'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded larning.py')

from resources import create_resource_directory
from define import value_list,option_widths
from data_collection import informations_basepath,details_basepath,label_filepath
from recog import option_trimsize,number_trimsize,informations_areas,details_areas
from larning import create_masks_directory,larning

larningbase_direpath = 'larning'
mask_images_dirpath = os.path.join(larningbase_direpath, 'mask_images')

class Collection():
    def __init__(self, key, informations, details, label):
        self.key = key
        self.informations = informations
        self.details = details
        self.label = label

def load_collections():
    with open(label_filepath) as f:
        labels = json.load(f)

    keys = [*labels.keys()]
    print(f"label count: {len(keys)}")

    collections = []
    for key in keys:
        filename = f'{key}.png'

        i_filepath = os.path.join(informations_basepath, filename)
        if os.path.isfile(i_filepath):
            i_image = Image.open(i_filepath)
        else:
            i_image = None

        d_filepath = os.path.join(details_basepath, filename)
        if os.path.isfile(d_filepath):
            d_image = Image.open(d_filepath)
        else:
            d_image = None

        collections.append(Collection(filename, i_image, d_image, labels[key]))
    
    return collections

if __name__ == '__main__':
    if len(argv) == 1:
        print('please argment.')
        exit()

    collections = load_collections()

    if not os.path.exists(larningbase_direpath):
        os.mkdir(larningbase_direpath)

    if not os.path.exists(mask_images_dirpath):
        os.mkdir(mask_images_dirpath)

    create_resource_directory()
    create_masks_directory()

    play_modes = {}
    for key in value_list['play_modes']:
        play_modes[key] = {}
    
    difficulties = {}
    levels = {}
    for key_d in value_list['difficulties']:
        difficulties[key_d] = {}
        for key_l in value_list['levels']:
            levels[f'{key_d}-{key_l}'] = {}
    
    option_value_list = [
        *value_list['options_arrange'],
        *value_list['options_arrange_dp'],
        *value_list['options_arrange_sync'],
        *value_list['options_flip'],
        *value_list['options_assist'],
        'BATTLE',
        'H-RANDOM'
    ]
    options = {}
    for key in option_value_list:
        options[key] = {}

    clear_types = {}
    for key in value_list['clear_types']:
        clear_types[key] = {}
    
    dj_levels = {}
    for key in value_list['dj_levels']:
        dj_levels[key] = {}
    
    numbers = {}
    for key in range(10):
        numbers[str(key)] = {}
    
    news = {}
    
    for collection in collections:
        label = collection.label
        if collection.informations is not None:
            image = collection.informations
            if label['play_mode'] != '':
                crop = image.crop(informations_areas['play_mode'])
                play_modes[label['play_mode']][collection.key] = crop
            if label['difficulty'] != '':
                crop = image.crop(informations_areas['difficulty'])
                difficulties[label['difficulty']][collection.key] = crop
                if label['level'] != '':
                    key = f"{label['difficulty']}-{label['level']}"
                    crop = image.crop(informations_areas['level'])
                    levels[key][collection.key] = crop
        if collection.details is not None:
            image = collection.details
            option_image = image.crop(details_areas['option'])
            left = 0
            if 'option_battle' in label.keys() and label['option_battle']:
                area = [left, 0, left + option_trimsize[0], option_trimsize[1]]
                options['option_battle'][collection.key] = option_image.crop(area)
                left += option_widths['BATTLE']
            if 'option_arrange' in label.keys() and label['option_arrange'] != '':
                key = label['option_arrange']
                area = [left, 0, left + option_trimsize[0], option_trimsize[1]]
                options[key][collection.key] = option_image.crop(area)
                left += option_widths[key]
            if 'option_arrange_dp' in label.keys() and label['option_arrange_dp'] != '/':
                key = label['option_arrange_dp']
                area = [left, 0, left + option_trimsize[0], option_trimsize[1]]
                options[key][collection.key] = option_image.crop(area)
                left += option_widths[key]
            if 'option_arrange_sync' in label.keys() and label['option_arrange_sync'] != '':
                key = label['option_arrange_sync']
                area = [left, 0, left + option_trimsize[0], option_trimsize[1]]
                options[key][collection.key] = option_image.crop(area)
                left += option_widths[key]
            if 'option_h-random' in label.keys() and label['option_h-random']:
                area = [left, 0, left + option_trimsize[0], option_trimsize[1]]
                options['option_h-random'][collection.key] = option_image.crop(area)
                left += option_widths['h-random']
            if 'option_flip' in label.keys() and label['option_flip'] != '':
                key = label['option_flip']
                area = [left, 0, left + option_trimsize[0], option_trimsize[1]]
                options[key][collection.key] = option_image.crop(area)
                left += option_widths[key]
            if 'option_assist' in label.keys() and label['option_assist'] != '':
                key = label['option_assist']
                area = [left, 0, left + option_trimsize[0], option_trimsize[1]]
                options[key][collection.key] = option_image.crop(area)
                left += option_widths[key]
            if 'clear_type' in label.keys() and label['clear_type'] != '':
                if label['clear_type'] != 'F-COMBO':
                    crop = image.crop(details_areas['clear_type'])
                    clear_types[label['clear_type']][collection.key] = crop
            if 'dj_level' in label.keys() and label['dj_level'] != '':
                crop = image.crop(details_areas['dj_level'])
                dj_levels[label['dj_level']][collection.key] = crop
            trimareas = []
            for i in range(4):
                trimareas.append([
                    int(i * number_trimsize[0]),
                    0,
                    int((i + 1) * number_trimsize[0]),
                    number_trimsize[1]
                ])
            for key in ['score', 'miss_count']:
                if key in label.keys() and label[key] != '':
                    crop1 = image.crop(details_areas[key])
                    value = int(label[key])
                    digit = 1
                    while int(value) > 0 or digit == 1:
                        number = str(int(value % 10))
                        crop2 = crop1.crop(trimareas[4-digit])
                        numbers[number][f"{key}-{digit}-{collection.key}"] = crop2
                        value /= 10
                        digit += 1
            for key in ['clear_type_new', 'dj_level_new', 'score_new', 'miss_count_new']:
                if key in label.keys() and not label[key]:
                    news[f"{key}-{collection.key}"] = image.crop(details_areas[key])

    if '-playmode' in argv:
        for key in play_modes.keys():
            larning(key, play_modes[key])

    if '-difficulty' in argv:
        for key in difficulties.keys():
            larning(key, difficulties[key])

    if '-level' in argv:
        for key in levels.keys():
            larning(key, levels[key])
    
    if '-option' in argv:
        for key in options.keys():
            larning(key, options[key])

    if '-cleartype' in argv:
        for key in clear_types.keys():
            larning(key, clear_types[key])

    if '-djlevel' in argv:
        for key in dj_levels.keys():
            larning(key, dj_levels[key])

    if '-numbers' in argv:
        for key in numbers.keys():
            larning(key, numbers[key])

    if '-new' in argv:
        larning('new', news)
