import PySimpleGUI as sg
import glob
import os
import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename='log.txt',
    filemode='w',
    format='%(asctime)s - %(name)s %(levelname)-7s %(message)s'
)

logger = logging.getLogger()

logger.debug('loaded manage.py')

import gui.manage as gui
from screenshot import Screenshot,open_screenimage
from resources_learning import RawLabel,raws_basepath

screenshot = Screenshot()

screen = None
screens = {}
screens_filename = []

def screenshot_process():
    if screen is None:
        return
    
    gui.display_image(screen.original)
    gui.set_labels(labels.get(screen.filename))

if __name__ == '__main__':
    labels = RawLabel()
    
    files = glob.glob(os.path.join(raws_basepath, '*.png'))
    filenames = [*map(os.path.basename, files)]

    window = gui.generate_window(filenames)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT):
            break
        if event == 'list_screens':
            if values['list_screens'][0] in screens:
                screen = screens[values['list_screens'][0]]
            else:
                filepath = os.path.join(raws_basepath, values['list_screens'][0])
                sc = open_screenimage(filepath)
                if not sc is None:
                    screen = sc
                    screens[values['list_screens'][0]] = screen
            screenshot_process()
        if event == 'button_label_overwrite' and not screen is None:
            screen_name = None
            for key in ['none', 'loading', 'music_select', 'playing', 'result']:
                if values[f'screen_{key}']:
                    screen_name = key

            graph = None
            for key in ['gauge', 'lanes', 'measures']:
                if values[f'graph_{key}']:
                    graph = key

            labels.update(
                screen.filename,
                {
                    'screen': screen_name,
                    'is_savable': values['is_savable'],
                    'rival': values['rival'],
                    'graphtype': graph,
                    'play_mode': values['play_mode'],
                    'play_side': values['play_side'],
                    'dead': values['dead']
                }
            )
            labels.save()
        if event == 'search_all':
            window['list_screens'].update(filenames)
        if event == 'search_only_music_select':
            targets = [filename for filename in filenames if labels.get(filename) is not None and 'screen' in labels.get(filename).keys() and labels.get(filename)['screen'] == 'music_select']
            window['list_screens'].update(targets)
        if event == 'search_only_playing':
            targets = [filename for filename in filenames if labels.get(filename) is not None and 'screen' in labels.get(filename).keys() and labels.get(filename)['screen'] == 'playing']
            window['list_screens'].update(targets)
        if event == 'search_only_result':
            targets = [filename for filename in filenames if labels.get(filename) is not None and 'screen' in labels.get(filename).keys() and labels.get(filename)['screen'] == 'result']
            window['list_screens'].update(targets)
        if event == 'search_only_no_annotation':
            targets = [filename for filename in filenames if labels.get(filename) is None]
            window['list_screens'].update(targets)

    window.close()
