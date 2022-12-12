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
from resources import areas,finds,save_find_image
from define import option_widths
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
    for key in finds.keys():
        box = pgui.locate(finds[key]['image'], screen.image, grayscale=True)
        area = areas['find'][key]
        result = False
        if not box is None and box.left == area[0] and box.top == area[1]:
            result = True
        window[f'find_{key}'].update(visible=result)

if __name__ == '__main__':
    labels = RawLabel()
    
    files = glob.glob(os.path.join(raws_basepath, '*.bmp'))
    filenames = [*map(os.path.basename, files)]

    window = gui.generate_window([*areas.keys()], filenames)

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
            if type(areas[values['area_top']]) is list:
                window['area_second'].update(visible=False)
                gui.set_area(areas[values['area_top']])
            else:
                window['area_second'].update(values=[*areas[values['area_top']].keys()], visible=True)
            window['button_find_save'].update(visible=(values['area_top'] == 'find'))
        if event == 'area_second':
            gui.set_area(areas[values['area_top']][values['area_second']])
            gui.switch_option_widths_view()
        if event == 'button_find_save' and not screen is None:
            if values['area_top'] == 'find':
                area = [int(value) for value in [values['left'], values['top'], values['right'], values['bottom']]]
                if area[0] < area[2] and area[1] < area[3]:
                    trim = screen.image.crop(area)
                    save_find_image(values['area_second'], trim)
                    gui.update_image(f"find_{values['area_second']}", trim)
        if event == 'button_trim' and not screen is None:
            image = screen.original
            area = [int(value) for value in [values['left'], values['top'], values['right'], values['bottom']]]
            if area[0] < area[2] and area[1] < area[3]:
                if values['area_second'] == 'option':
                    for number in range(1,4):
                        option = values[f'area_option{number}']
                        delimita = values[f'area_delimita{number}']
                        if option != '' and delimita != '':
                            area[0] += option_widths[option] + option_widths[delimita]
                            area[2] += option_widths[option] + option_widths[delimita]
                gui.display_trim(image.crop(area))
        if event == 'button_label_overwrite' and not screen is None:
            playside = None
            if values['play_side_none']:
                playside = ''
            if values['play_side_1p']:
                playside = '1P'
            if values['play_side_2p']:
                playside = '2P'

            labels.update(
                screen.filename,
                {
                    'starting': values['starting'],
                    'trigger': values['trigger'],
                    'cutin_mission': values['cutin_mission'],
                    'cutin_bit': values['cutin_bit'],
                    'rival': values['rival'],
                    'play_side': playside
                }
            )
            labels.save()
        if event == 'button_feedback' and not screen is None:
            gui.feedback()

    window.close()
