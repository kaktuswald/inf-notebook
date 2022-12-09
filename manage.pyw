import PySimpleGUI as sg
import pyautogui as pgui
import io
import glob
import os
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

import gui.manage as gui
from resources import areas,finds,masks,save_areas,save_find_image
from define import value_list,option_widths
from recog import recog
from labels import larning_source_label
from screenshot import Screenshot

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
    labels = larning_source_label()
    
    images = {}
    for key in ['loading', 'music_select', 'result']:
        if key in finds.keys():
            bytes = io.BytesIO()
            finds[key]['image'].save(bytes, format='PNG')
            images[f'find_{key}'] = bytes.getvalue()
        else:
            images[f'find_{key}'] = None

    for key in ['trigger', 'cutin_mission', 'cutin_bit']:
        image = Image.fromarray(masks[key].value)
        bytes = io.BytesIO()
        image.save(bytes, format='PNG')
        images[key] = bytes.getvalue()

    files = glob.glob('larning_sources/*.png')
    filenames = [*map(os.path.basename, files)]

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

    window = gui.generate_window([*areas.keys()], selectable_value_list, images, filenames)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT):
            break
        if event == 'list_screens':
            if values['list_screens'][0] in screens:
                screen = screens[values['list_screens'][0]]
            else:
                filepath = os.path.join('larning_sources', values['list_screens'][0])
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
        if event == 'button_define_overwrite':
            area = [int(value) for value in [values['left'], values['top'], values['right'], values['bottom']]]

            if type(areas[values['key1']]) is list:
                areas[values['key1']] = area
            else:
                if type(areas[values['key1']][values['key2']]) is list:
                    areas[values['key1']][values['key2']] = area
                else:
                    areas[values['key1']][values['key2']][values['key3']] = area
            
            save_areas()
        if event == 'button_label_overwrite' and not screen is None:
            playside = None
            if values['play_side_none']:
                playside = ''
            if values['play_side_1p']:
                playside = '1P'
            if values['play_side_2p']:
                playside = '2P'

            use_option = False
            for key in ['option_arrange', 'option_arrange_1p', 'option_arrange_2p', 'option_arrange_sync', 'option_flip', 'option_assist']:
                if values[key] != '':
                    use_option = True
            for key in ['option_battle', 'option_h-random']:
                if values[key]:
                    use_option = True
            
            labels.update(
                screen.filename,
                {
                    'starting': values['starting'],
                    'trigger': values['trigger'],
                    'cutin_mission': values['cutin_mission'],
                    'cutin_bit': values['cutin_bit'],
                    'rival': values['rival'],
                    'play_mode': values['play_mode'],
                    'difficulty': values['difficulty'],
                    'level': values['level'],
                    'music': values['music'],
                    'play_side': playside,
                    'use_option': use_option,
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
            )
            labels.save()
        if event == 'button_recog' and not screen is None:
            if recog.is_result(screen.image):
                gui.set_result(recog.get_result(screen))

    window.close()
