import os
from sys import argv,exit
from logging import getLogger
import numpy as np

logger_child_name = 'larning'

logger = getLogger().getChild(logger_child_name)
logger.debug('loaded larning.py')

from resources import create_resource_directory
from define import define
from data_collection import load_collections
from larning import create_masks_directory,larning
from notes import larning_notes
from clear_type import larning_clear_type
from dj_level import larning_dj_level
from number_current import larning_number_current
from number_best import larning_number_best

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
    notes = {}
    
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

    clear_types = {}
    dj_levels = {}
    numbers_best = {}
    numbers_current = {}
    
    news = {}
    
    for collection in collections:
        label = collection.label
        if collection.informations is not None:
            image = collection.informations
            if label['informations']['play_mode'] != '':
                crop = image.crop(define.informations_areas['play_mode'])
                play_modes[label['informations']['play_mode']][collection.key] = crop
            if label['informations']['difficulty'] != '':
                crop = image.crop(define.informations_areas['difficulty'])
                difficulties[label['informations']['difficulty']][collection.key] = crop
                if label['informations']['level'] != '':
                    key = f"{label['informations']['difficulty']}-{label['informations']['level']}"
                    crop = image.crop(define.informations_areas['level'])
                    levels[key][collection.key] = crop
            if 'notes' in label['informations'] and label['informations']['notes'] != '':
                cropped_value = image.crop(define.informations_areas['notes'])
                value = int(label['informations']['notes'])
                digit = 1
                while int(value) > 0 or digit == 1:
                    number = int(value % 10)
                    cropped_number = cropped_value.crop(define.notes_trimareas[4-digit])
                    notes[f'{collection.key}_{digit}_{number}'] = {
                        'value': number,
                        'np': np.array(cropped_number)
                    }
                    value /= 10
                    digit += 1
        if collection.details is not None:
            image = collection.details

            if 'display' in label['details'].keys() and not label['details']['display'] in ['', 'default']:
                key = f"graph_{label['details']['display']}"
                crop = image.crop(define.details_areas[key])
                graphs[key][collection.key] = crop

            option_image = image.crop(define.details_areas['option'])
            left = 0
            if label['details']['option_battle']:
                area = [left, 0, left + define.option_trimsize[0], define.option_trimsize[1]]
                options['BATTLE'][collection.key] = option_image.crop(area)
                left += define.option_widths['BATTLE'] + define.option_widths[',']
            if label['details']['option_arrange'] != '':
                key = label['details']['option_arrange']
                area = [left, 0, left + define.option_trimsize[0], define.option_trimsize[1]]
                options[key][collection.key] = option_image.crop(area)
                left += define.option_widths[key] + define.option_widths[',']
            if label['details']['option_arrange_dp'] != '/':
                key_left, key_right = label['details']['option_arrange_dp'].split('/')
                area = [left, 0, left + define.option_trimsize[0], define.option_trimsize[1]]
                options[key_left][collection.key] = option_image.crop(area)
                left += define.option_widths[key_left] + define.option_widths['/']
                area = [left, 0, left + define.option_trimsize[0], define.option_trimsize[1]]
                options[key_right][collection.key] = option_image.crop(area)
                left += define.option_widths[key_right] + define.option_widths[',']
            if label['details']['option_arrange_sync'] != '':
                key = label['details']['option_arrange_sync']
                area = [left, 0, left + define.option_trimsize[0], define.option_trimsize[1]]
                options[key][collection.key] = option_image.crop(area)
                left += define.option_widths[key] + define.option_widths[',']
            if label['details']['option_flip'] != '':
                key = label['details']['option_flip']
                area = [left, 0, left + define.option_trimsize[0], define.option_trimsize[1]]
                options[key][collection.key] = option_image.crop(area)
                left += define.option_widths[key] + define.option_widths[',']
            if label['details']['option_assist'] != '':
                key = label['details']['option_assist']
                area = [left, 0, left + define.option_trimsize[0], define.option_trimsize[1]]
                options[key][collection.key] = option_image.crop(area)

            for key in ['best', 'current']:
                key_clear_type = f'clear_type_{key}'
                if key_clear_type in label['details'] and label['details'][key_clear_type] != '':
                    clear_types[f'{collection.key}_{key}'] = {
                        'value': label['details'][key_clear_type],
                        'np': np.array(image.crop(define.details_areas['clear_type'][key])),
                    }

                key_dj_level = f'dj_level_{key}'
                if key_dj_level in label['details'] and label['details'][key_dj_level] != '':
                    dj_levels[f'{collection.key}_{key}'] = {
                        'value': label['details'][key_dj_level],
                        'np': np.array(image.crop(define.details_areas['dj_level'][key])),
                    }

            for key in ['score', 'miss_count']:
                key_best = f'{key}_best'
                if key_best in label['details'] and label['details'][key_best] != '':
                    crop1 = image.crop(define.details_areas[key]['best'])
                    value = int(label['details'][key_best])
                    digit = 1
                    while int(value) > 0 or digit == 1:
                        number = int(value % 10)
                        crop2 = crop1.crop(define.number_best_trimareas[4-digit])
                        numbers_best[f"{key_best}-{digit}-{collection.key}"] = {
                            'value': number,
                            'np': np.array(crop2)
                        }
                        value /= 10
                        digit += 1

                key_current = f'{key}_current'
                if key_current in label['details'] and label['details'][key_current] != '':
                    crop1 = image.crop(define.details_areas[key]['current'])
                    value = int(label['details'][key_current])
                    digit = 1
                    while int(value) > 0 or digit == 1:
                        number = int(value % 10)
                        crop2 = crop1.crop(define.number_current_trimareas[4-digit])
                        numbers_current[f"{key_current}-{digit}-{collection.key}"] = {
                            'value': number,
                            'np': np.array(crop2)
                        }
                        value /= 10
                        digit += 1

            for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
                if label['details'][f'{key}_new']:
                    news[f"{key}-{collection.key}"] = image.crop(define.details_areas[key]['new'])

    if '-all' in argv or '-playmode' in argv:
        for key in play_modes.keys():
            larning(key, play_modes[key])

    if '-all' in argv or '-difficulty' in argv:
        for key in difficulties.keys():
            larning(key, difficulties[key])

    if '-all' in argv or '-level' in argv:
        for key in levels.keys():
            larning(key, levels[key])

    if '-all' in argv or '-notes' in argv:
        larning_notes(notes)
    
    if '-all' in argv or '-graph' in argv:
        for key in graphs.keys():
            larning(key, graphs[key])

    if '-all' in argv or '-option' in argv:
        for key in options.keys():
            larning(key, options[key])

    if '-all' in argv or '-cleartype' in argv:
        larning_clear_type(clear_types)

    if '-all' in argv or '-djlevel' in argv:
        larning_dj_level(dj_levels)

    if '-all' in argv or '-number' in argv:
        larning_number_best(numbers_best)
        larning_number_current(numbers_current)

    if '-all' in argv or '-new' in argv:
        larning('new', news)
