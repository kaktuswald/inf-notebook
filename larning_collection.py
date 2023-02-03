import os
from sys import argv,exit
from logging import getLogger

logger_child_name = 'larning'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded larning.py')

from resources import create_resource_directory
from define import define
from data_collection import load_collections
from recog import option_trimsize,number_trimsize,informations_areas
from larning import create_masks_directory,larning

larningbase_direpath = 'larning'
mask_images_dirpath = os.path.join(larningbase_direpath, 'mask_images')

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
    for key in define.value_list['play_modes']:
        play_modes[key] = {}
    
    difficulties = {}
    levels = {}
    for key_d in define.value_list['difficulties']:
        difficulties[key_d] = {}
        for key_l in define.value_list['levels']:
            levels[f'{key_d}-{key_l}'] = {}
    
    graphs = {
        'graph_lanes': {},
        'graph_measures': {}
    }

    option_value_list = [
        *define.value_list['options_arrange'],
        *define.value_list['options_arrange_dp'],
        *define.value_list['options_arrange_sync'],
        *define.value_list['options_flip'],
        *define.value_list['options_assist'],
        'BATTLE',
        'H-RANDOM'
    ]
    options = {}
    for key in option_value_list:
        options[key] = {}

    dj_levels = {}
    for key in define.value_list['dj_levels']:
        dj_levels[key] = {}
    
    numbers = {}
    for key in range(10):
        numbers[str(key)] = {}
    
    news = {}
    
    for collection in collections:
        label = collection.label
        if collection.informations is not None:
            image = collection.informations
            if label['informations']['play_mode'] != '':
                crop = image.crop(informations_areas['play_mode'])
                play_modes[label['informations']['play_mode']][collection.key] = crop
            if label['informations']['difficulty'] != '':
                crop = image.crop(informations_areas['difficulty'])
                difficulties[label['informations']['difficulty']][collection.key] = crop
                if label['informations']['level'] != '':
                    key = f"{label['informations']['difficulty']}-{label['informations']['level']}"
                    crop = image.crop(informations_areas['level'])
                    levels[key][collection.key] = crop
        if collection.details is not None:
            image = collection.details

            if 'display' in label['details'].keys() and not label['details']['display'] in ['', 'default']:
                key = f"graph_{label['details']['display']}"
                crop = image.crop(define.details_areas[key])
                graphs[key][collection.key] = crop

            option_image = image.crop(define.details_areas['option'])
            left = 0
            if label['details']['option_battle']:
                area = [left, 0, left + option_trimsize[0], option_trimsize[1]]
                options['BATTLE'][collection.key] = option_image.crop(area)
                left += define.option_widths['BATTLE'] + define.option_widths[',']
            if label['details']['option_arrange'] != '':
                key = label['details']['option_arrange']
                area = [left, 0, left + option_trimsize[0], option_trimsize[1]]
                options[key][collection.key] = option_image.crop(area)
                left += define.option_widths[key] + define.option_widths[',']
            if label['details']['option_arrange_dp'] != '/':
                key_left, key_right = label['details']['option_arrange_dp'].split('/')
                area = [left, 0, left + option_trimsize[0], option_trimsize[1]]
                options[key_left][collection.key] = option_image.crop(area)
                left += define.option_widths[key_left] + define.option_widths['/']
                area = [left, 0, left + option_trimsize[0], option_trimsize[1]]
                options[key_right][collection.key] = option_image.crop(area)
                left += define.option_widths[key_right] + define.option_widths[',']
            if label['details']['option_arrange_sync'] != '':
                key = label['details']['option_arrange_sync']
                area = [left, 0, left + option_trimsize[0], option_trimsize[1]]
                options[key][collection.key] = option_image.crop(area)
                left += define.option_widths[key] + define.option_widths[',']
            if label['details']['option_flip'] != '':
                key = label['details']['option_flip']
                area = [left, 0, left + option_trimsize[0], option_trimsize[1]]
                options[key][collection.key] = option_image.crop(area)
                left += define.option_widths[key] + define.option_widths[',']
            if label['details']['option_assist'] != '':
                key = label['details']['option_assist']
                area = [left, 0, left + option_trimsize[0], option_trimsize[1]]
                options[key][collection.key] = option_image.crop(area)

            if label['details']['dj_level'] != '':
                crop = image.crop(define.details_areas['dj_level'])
                dj_levels[label['details']['dj_level']][collection.key] = crop

            trimareas = []
            for i in range(4):
                trimareas.append([
                    int(i * number_trimsize[0]),
                    0,
                    int((i + 1) * number_trimsize[0]),
                    number_trimsize[1]
                ])
            for key in ['score', 'miss_count']:
                if label['details'][key] != '':
                    crop1 = image.crop(define.details_areas[key])
                    value = int(label['details'][key])
                    digit = 1
                    while int(value) > 0 or digit == 1:
                        number = str(int(value % 10))
                        crop2 = crop1.crop(trimareas[4-digit])
                        numbers[number][f"{key}-{digit}-{collection.key}"] = crop2
                        value /= 10
                        digit += 1
            for key in ['clear_type_new', 'dj_level_new', 'score_new', 'miss_count_new']:
                if label['details'][key]:
                    news[f"{key}-{collection.key}"] = image.crop(define.details_areas[key])

    if '-playmode' in argv:
        for key in play_modes.keys():
            larning(key, play_modes[key])

    if '-difficulty' in argv:
        for key in difficulties.keys():
            larning(key, difficulties[key])

    if '-level' in argv:
        for key in levels.keys():
            larning(key, levels[key])
    
    if '-graph' in argv:
        for key in graphs.keys():
            larning(key, graphs[key])

    if '-option' in argv:
        for key in options.keys():
            larning(key, options[key])

    if '-djlevel' in argv:
        for key in dj_levels.keys():
            larning(key, dj_levels[key])

    if '-numbers' in argv:
        for key in numbers.keys():
            larning(key, numbers[key])

    if '-new' in argv:
        larning('new', news)
