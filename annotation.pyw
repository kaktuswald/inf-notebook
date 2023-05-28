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
import data_collection as dc

images = {}
labels = {}
target_key = None

def update_annotation():
    global labels

def load_image(basedir, key):
    filename = f'{key}.png'
    filepath = os.path.join(basedir, filename)

    if not os.path.exists(filepath):
        return None

    return Image.open(filepath)

if __name__ == '__main__':
    if os.path.exists(dc.label_filepath):
        with open(dc.label_filepath) as f:
            labels = json.load(f)
    
    logger.debug(f'current annotation count: {len(labels)}')
    
    for filepath in glob(os.path.join(dc.informations_basepath, '*')):
        key = os.path.basename(filepath).removesuffix('.png')
        images[key] = None
    for filepath in glob(os.path.join(dc.details_basepath, '*')):
        key = os.path.basename(filepath).removesuffix('.png')
        images[key] = None

    window = gui.generate_window([*images.keys()])

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT):
            break
        if event == 'list_keys':
            target_key = values['list_keys'][0]
            if images[target_key] is None:
                images[target_key] = {
                    'informations': load_image(dc.informations_basepath, target_key),
                    'details': load_image(dc.details_basepath, target_key)
                }
            
            informations = images[target_key]['informations']
            details = images[target_key]['details']

            gui.set_labels(labels[target_key] if target_key in labels else {})
            gui.display_informations(informations)
            gui.display_details(details)

            if informations is not None:
                gui.set_informations(images[target_key]['informations'])
            else:
                gui.reset_informations()
            if details is not None:
                gui.set_details(images[target_key]['details'])
            else:
                gui.reset_details()
        
        if event == 'button_label_overwrite' and not target_key is None:
            if values['has_informations']:
                informations = {
                    'play_mode': values['play_mode'],
                    'difficulty': values['difficulty'],
                    'level': values['level'],
                    'notes': values['notes'],
                    'music': values['music'],
                }
            else:
                informations = None
            
            if values['has_details']:
                graphtype = ""
                for key in ['gauge', 'lanes', 'measures']:
                    if values[f'graphtype_{key}']:
                        graphtype = key

                details = {
                    'graphtype': graphtype,
                    'option_arrange': values['option_arrange'],
                    'option_arrange_dp': f"{values['option_arrange_1p']}/{values['option_arrange_2p']}",
                    'option_arrange_sync': values['option_arrange_sync'],
                    'option_flip': values['option_flip'],
                    'option_assist': values['option_assist'],
                    'option_battle': values['option_battle'],
                    'clear_type_best': values['clear_type_best'],
                    'clear_type_current': values['clear_type_current'],
                    'clear_type_new': values['clear_type_new'],
                    'dj_level_best': values['dj_level_best'],
                    'dj_level_current': values['dj_level_current'],
                    'dj_level_new': values['dj_level_new'],
                    'score_best': values['score_best'],
                    'score_current': values['score_current'],
                    'score_new': values['score_new'],
                    'miss_count_best': values['miss_count_best'],
                    'miss_count_current': values['miss_count_current'],
                    'miss_count_new': values['miss_count_new'],
                    'graphtarget': values['graphtarget']
                }
            else:
                details = None
            
            labels[target_key] = {
                'informations': informations,
                'details': details
            }

            with open(dc.label_filepath, 'w') as f:
                json.dump(labels, f, indent=2)
        if event == 'button_recog' and not target_key is None:
            gui.set_result()
        if event == 'has_informations':
            gui.switch_has_informations()
        if event == 'has_details':
            gui.switch_has_details()
        if event in ['only_not_annotation', 'only_undefined_music', 'only_full_combo', 'keyfilter']:
            gui.change_search_condition(images.keys(), labels)

    window.close()
