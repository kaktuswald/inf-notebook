import PySimpleGUI as sg
import json
import os
from glob import glob
from PIL import Image
import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename='log.txt',
    filemode='w',
    format='%(asctime)s - %(name)s %(levelname)-7s %(message)s'
)

logger = logging.getLogger()

logger.debug('loaded manage.py')

import gui.annotation as gui
from define import value_list

collection_basepath = 'collection_data'

annotations_filepath = os.path.join(collection_basepath, 'annotations.json')
informations_basepath = os.path.join(collection_basepath, 'informations')
details_basepath = os.path.join(collection_basepath, 'details')

images = {}
annotations = {}
target_key = None

def update_annotation():
    global annotations

def load_image(basedir, key):
    filename = f'{key}.png'
    filepath = os.path.join(basedir, filename)

    if not os.path.exists(filepath):
        return None

    return Image.open(filepath)

if __name__ == '__main__':
    if os.path.exists(annotations_filepath):
        with open(annotations_filepath) as f:
            annotations = json.load(f)
    
    logger.debug(f'current annotation count: {len(annotations)}')
    
    for filepath in glob(os.path.join(informations_basepath, '*')):
        key = os.path.basename(filepath).replace('.png', '')
        images[key] = None
    for filepath in glob(os.path.join(details_basepath, '*')):
        key = os.path.basename(filepath).replace('.png', '')
        images[key] = None

    selectable_value_list = {}
    for key, values in value_list.items():
        selectable_value_list[key] = ['', *values]
    selectable_value_list['all_options'] = [
        '',
        *value_list['options_arrange'],
        *value_list['options_arrange_dp'],
        *value_list['options_arrange_sync'],
        *value_list['options_flip'],
        *value_list['options_assist'],
        'BATTLE',
        'H-RANDOM'
    ]
    selectable_value_list['delimita'] = ['', ',', '/']

    window = gui.generate_window(selectable_value_list, [*images.keys()])

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT):
            break
        if event == 'list_keys':
            target_key = values['list_keys'][0]
            if images[target_key] is None:
                images[target_key] = {
                    'informations': load_image(informations_basepath, target_key),
                    'details': load_image(details_basepath, target_key)
                }
            
            informations = images[target_key]['informations']
            details = images[target_key]['details']

            gui.set_labels(annotations[target_key] if target_key in annotations else{})
            gui.display_informations(informations)
            gui.display_details(details)

            if informations is not None:
                gui.set_informations(images[target_key]['informations'])
            if details is not None:
                gui.set_details(images[target_key]['details'])
        
        if event == 'button_label_overwrite' and not target_key is None:
            annotations[target_key] = {
                'play_mode': values['play_mode'],
                'difficulty': values['difficulty'],
                'level': values['level'],
                'music': values['music'],
                'option_arrange': values['option_arrange'],
                'option_arrange_dp': f"{values['option_arrange_1p']}/{values['option_arrange_2p']}",
                'option_arrange_sync': values['option_arrange_sync'],
                'option_flip': values['option_flip'],
                'option_assist': values['option_assist'],
                'option_battle': values['option_battle'],
                'option_h-random': values['option_h-random'],
                'clear_type': values['clear_type'],
                'dj_level': values['dj_level'],
                'score': values['score'],
                'miss_count': values['miss_count'],
                'clear_type_new': values['clear_type_new'],
                'dj_level_new': values['dj_level_new'],
                'score_new': values['score_new'],
                'miss_count_new': values['miss_count_new']
            }
            with open(annotations_filepath, 'w') as f:
                json.dump(annotations, f, indent=2)
        if event == 'button_recog' and not target_key is None:
            gui.set_result()

    window.close()
