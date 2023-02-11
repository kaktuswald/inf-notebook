import PySimpleGUI as sg
import pyautogui as pgui
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
from resources import find_images
from define import define
from screenshot import Screenshot
from larning import RawLabel,raws_basepath

screenshot = Screenshot()

screen = None
screens = {}
screens_filename = []

def screenshot_process():
    if screen is None:
        return
    
    gui.display_image(screen.original)
    gui.set_labels(labels.get(screen.filename))

    find()
    gui.set_recognition(screen)

def find():
    window['result_screen'].update('')
    for key in find_images.keys():
        box = pgui.locate(find_images[key], screen.monochrome, grayscale=True)
        area = define.areas[key]
        if not box is None and box.left == area[0] and box.top == area[1]:
            window['result_screen'].update(key)
            window['result_screen_masterpos'].update(f'{area[0]}, {area[1]}')
            window['result_screen_findpos'].update(f'{box.left}, {box.top}')

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
                sc = screenshot.open(filepath)
                if not sc is None:
                    screen = sc
                    screens[values['list_screens'][0]] = screen
            screenshot_process()
        if event == 'area_top':
            if type(define.areas[values['area_top']]) is list:
                window['area_second'].update(visible=False)
                gui.set_area(define.areas[values['area_top']])
            else:
                window['area_second'].update(values=[*define.areas[values['area_top']].keys()], visible=True)
        if event == 'area_second':
            gui.set_area(define.areas[values['area_top']][values['area_second']])
            gui.switch_option_widths_view()
        if event == 'button_trim' and not screen is None:
            image = screen.original
            area = [int(value) for value in [values['left'], values['top'], values['right'], values['bottom']]]
            if area[0] < area[2] and area[1] < area[3]:
                if values['area_second'] == 'option':
                    for number in range(1,4):
                        option = values[f'area_option{number}']
                        delimita = values[f'area_delimita{number}']
                        if option != '' and delimita != '':
                            area[0] += define.option_widths[option] + define.option_widths[delimita]
                            area[2] += define.option_widths[option] + define.option_widths[delimita]
                gui.display_trim(image.crop(area))
        if event == 'button_label_overwrite' and not screen is None:
            screen_name = None
            for key in ['none', 'loading', 'music_select', 'playing', 'result']:
                if values[f'screen_{key}']:
                    screen_name = key

            labels.update(
                screen.filename,
                {
                    'screen': screen_name,
                    'trigger': values['trigger'],
                    'cutin_mission': values['cutin_mission'],
                    'cutin_bit': values['cutin_bit'],
                    'rival': values['rival'],
                    'play_mode': values['play_mode'],
                    'play_side': values['play_side'],
                    'dead': values['dead']
                }
            )
            labels.save()
        if event == 'button_feedback' and not screen is None:
            gui.feedback()
        if event == 'search_all':
            window['list_screens'].update(filenames)
        if event == 'search_only_result':
            targets = [filename for filename in filenames if labels.get(filename) is not None and 'screen' in labels.get(filename).keys() and labels.get(filename)['screen'] == 'result']
            window['list_screens'].update(targets)

    window.close()
