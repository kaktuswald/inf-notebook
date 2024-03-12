import PySimpleGUI as sg
import json
from os.path import exists,join,basename
from PIL import Image
import logging
import numpy as np
from glob import glob

logging.basicConfig(
    level=logging.DEBUG,
    filename='log.txt',
    filemode='w',
    format='%(asctime)s - %(name)s %(levelname)-7s %(message)s'
)

logger = logging.getLogger()

logger.debug('loaded manage.py')

import gui.annotation_musicselect as gui
from resources_larning_musicselect import images_musicselect_basepath,label_filepath

images = {}
np_values = {}
labels = {}
target_key = None

def update_annotation():
    global labels

def load_image(filename):
    filepath = join(images_musicselect_basepath, filename)

    if not exists(filepath):
        return None

    return Image.open(filepath)

if __name__ == '__main__':
    files = glob(join(images_musicselect_basepath, '*.png'))
    filenames = [*map(basename, files)]

    try:
        with open(label_filepath) as f:
            labels = json.load(f)
    except Exception:
        labels = {}

    logger.debug(f'current annotation count: {len(labels)}')
    
    window = gui.generate_window(filenames)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT):
            break
        if event == 'list_keys':
            target_key = values['list_keys'][0]
            if not target_key in images.keys() or images[target_key] is None:
                image = load_image(target_key)
                np_values[target_key] = np.array(image)
                images[target_key] = image.resize(gui.imagesize)
            
            if target_key in labels.keys():
                gui.set_labels(labels[target_key])
            else:
                gui.clear_labels()

            gui.clear_results()
            gui.display_image(images[target_key])
            if target_key in images.keys():
                gui.recognize(np_values[target_key])

        if event == 'button_label_overwrite' and not target_key is None:
            labels[target_key] = {
                'playmode': values['playmode'],
                'difficulty': values['difficulty'],
                'level_beginner': values['level_beginner'],
                'level_normal': values['level_normal'],
                'level_hyper': values['level_hyper'],
                'level_another': values['level_another'],
                'level_leggendaria': values['level_leggendaria'],
                'version': values['version'],
                'musictype': values['musictype'],
                'musicname': values['musicname'],
                'cleartype': values['cleartype'],
                'djlevel': values['djlevel'],
                'score': values['score'],
                'misscount': values['misscount'],
            }

            with open(label_filepath, 'w') as f:
                json.dump(labels, f, indent=2)
        if event == 'button_recog' and not target_key is None:
            gui.reflect_recognized()
        if event in ['only_not_annotation', 'only_undefined_musicname', 'only_undefined_version', 'keyfilter']:
            gui.change_search_condition(filenames, labels)

    window.close()
