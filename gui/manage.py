import PySimpleGUI as sg
import io
from PIL import Image

from define import value_list
from resources import finds,masks
from recog import recog
from .static import title,icon_path

default_box = (0, 0, 1280, 720)
scales = ['1/1', '1/2', '1/4']

def layout_manage(area_names, filenames):
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

    images = {}
    for key in ['loading', 'music_select', 'result']:
        if key in finds.keys():
            bytes = io.BytesIO()
            finds[key]['image'].save(bytes, format='PNG')
            images[f'find_{key}'] = bytes.getvalue()
        else:
            images[f'find_{key}'] = None

    for key in ['trigger', 'cutin_mission', 'cutin_bit', 'rival']:
        image = Image.fromarray(masks[key].value)
        bytes = io.BytesIO()
        image.save(bytes, format='PNG')
        images[key] = bytes.getvalue()

    area_define = [
        [
            sg.Text('領域', size=(12, 1)),
            sg.Column([
                [sg.Combo(area_names, key='area_top', size=(11, 1), readonly=True, enable_events=True)],
                [sg.Combo([], key='area_second', size=(13, 1), readonly=True, enable_events=True)]
            ], background_color='#7799fd')
        ],
        [
            sg.Text('オプション幅', size=(12, 1)),
            sg.Column([
                [
                    sg.Combo(selectable_value_list['all_options'], key='area_option1', size=(11, 1), readonly=True, enable_events=True),
                    sg.Combo(selectable_value_list['delimita'], key='area_delimita1', size=(2, 1), readonly=True, enable_events=True)
                ],
                [
                    sg.Combo(selectable_value_list['all_options'], key='area_option2', size=(11, 1), readonly=True, enable_events=True),
                    sg.Combo(selectable_value_list['delimita'], key='area_delimita2', size=(2, 1), readonly=True, enable_events=True)
                ],
                [
                    sg.Combo(selectable_value_list['all_options'], key='area_option3', size=(11, 1), readonly=True, enable_events=True),
                    sg.Combo(selectable_value_list['delimita'], key='area_delimita3', size=(2, 1), readonly=True, enable_events=True)
                ]
            ], background_color='#7799fd'),
        ],
        [
            sg.Text('X1', size=(2, 1)), sg.Input(default_box[0], key='left', size=(4, 1)),
            sg.Text('Y1', size=(2, 1)), sg.Input(default_box[1], key='top', size=(4, 1))
        ],
        [
            sg.Text('X2', size=(2, 1)), sg.Input(default_box[2], key='right', size=(4, 1)),
            sg.Text('Y2', size=(2, 1)), sg.Input(default_box[3], key='bottom', size=(4, 1))
        ],
        [sg.Button('トリム', key='button_trim')],
        [sg.Image(key='trim')],
        [sg.Button('検索イメージ保存', key='button_find_save', visible=False)],
    ]

    manage_label_define = [
        [
            sg.Text('起動', size=(15, 1)),
            sg.Combo(selectable_value_list['startings'], key='starting', readonly=True)
        ],
        [
            sg.Text('リザルト判定', size=(15, 1)),
            sg.Checkbox('認識可能', key='trigger', default=True)
        ],
        [
            sg.Text('ミッション', size=(15, 1)),
            sg.Checkbox('カットイン', key='cutin_mission'),
        ],
        [
            sg.Text('ビット獲得', size=(15, 1)),
            sg.Checkbox('カットイン', key='cutin_bit')
        ],
        [
            sg.Text('ライバル挑戦状', size=(15, 1)),
            sg.Checkbox('表示中', key='rival', default=False)
        ],
        [
            sg.Text('プレイサイド', size=(15, 1)),
            sg.Radio('なし', key='play_side_none', group_id='play_side', default=True),
            sg.Radio('1P', key='play_side_1p', group_id='play_side'),
            sg.Radio('2P', key='play_side_2p', group_id='play_side')
        ],
        [
            sg.Button('アノテーション保存', key='button_label_overwrite'),
            sg.Button('認識結果から引用', key='button_feedback')
        ]
    ]

    manage_result = [
        [sg.Text('画面位置検索', size=(32, 1))],
        [
            sg.Text('ローディング', size=(20, 1)),
            sg.Image(data=images['find_loading'], visible=False, key='find_loading')
        ],
        [
            sg.Text('選曲', size=(20, 1)),
            sg.Image(data=images['find_music_select'], visible=False, key='find_music_select')
        ],
        [
            sg.Text('リザルト', size=(20, 1)),
            sg.Image(data=images['find_result'], visible=False, key='find_result')
        ],
        [sg.Text('起動認識', size=(32, 1))],
        [
            sg.Text('起動', size=(20, 1)),
            sg.Text(key='recog_starting', background_color='#7799fd', text_color='#000000')
        ],
        [sg.Text('リザルト認識', size=(32, 1))],
        [
            sg.Text('リザルト判定', size=(20, 1)),
            sg.Image(data=images['trigger'], visible=False, key='recog_trigger')
        ],
        [
            sg.Text('ミッションカットイン', size=(20, 1)),
            sg.Image(data=images['cutin_mission'], visible=False, key='recog_cutin_mission')
        ],
        [
            sg.Text('ビット獲得カットイン', size=(20, 1)),
            sg.Image(data=images['cutin_bit'], visible=False, key='recog_cutin_bit')
        ],
        [
            sg.Text('ライバル挑戦状', size=(22, 1)),
            sg.Image(data=images['rival'], visible=False, key='recog_rival')
        ],
        [
            sg.Text('プレイサイド', size=(22, 1)),
            sg.Text(key='recog_play_side', background_color='#7799fd', text_color='#000000')
        ]
    ]

    return [
        [
            sg.Column([
                [
                    sg.Column([
                        [sg.Text('画像表示スケール'), sg.Combo(scales, default_value='1/2', readonly=True, key='scale')],
                        [sg.Image(key='screenshot', size=(640, 360))]
                    ],pad=0),
                    sg.Listbox(filenames, key='list_screens', size=(27, 20), enable_events=True),
                ],
                [
                    sg.Column(area_define, size=(300, 350), background_color='#7799fd'),
                    sg.Column(manage_label_define, size=(360, 350), background_color='#7799fd'),
                    sg.Column(manage_result, size=(310, 350), background_color='#7799fd')
                ],
            ],pad=0)
        ],
    ]

def generate_window(area_names, filenames):
    global window

    window = sg.Window(
        title,
        layout_manage(area_names, filenames),
        icon=icon_path,
        grab_anywhere=True,
        return_keyboard_events=True,
        resizable=False,
        finalize=True,
        enable_close_attempted_event=True
    )

    window['area_second'].update(visible=False)
    window['area_option1'].update(visible=False)
    window['area_delimita1'].update(visible=False)
    window['area_option2'].update(visible=False)
    window['area_delimita2'].update(visible=False)
    window['area_option3'].update(visible=False)
    window['area_delimita3'].update(visible=False)

    return window

def change_display(key, value):
    window[key].update(visible=value)

def set_area(area):
        window['left'].update(area[0])
        window['top'].update(area[1])
        window['right'].update(area[2])
        window['bottom'].update(area[3])

def switch_option_widths_view():
    visible = window['area_second'].get() == 'option'

    window['area_option1'].update(visible=visible)
    window['area_delimita1'].update(visible=visible)
    window['area_option2'].update(visible=visible)
    window['area_delimita2'].update(visible=visible)
    window['area_option3'].update(visible=visible)
    window['area_delimita3'].update(visible=visible)

def display_image(image):
    scale = window['scale'].get()
    if scale == '1/2':
        image = image.resize((image.width // 2, image.height // 2))
    if scale == '1/4':
        image = image.resize((image.width // 3, image.height // 3))
    
    bytes = io.BytesIO()
    image.save(bytes, format='PNG')

    window['screenshot'].update(size=image.size, data=bytes.getvalue())

def display_trim(image):
    while image.width > 1920 / 8 or image.height > 1080 / 4:
        image = image.resize((image.width // 2, image.height // 2))
    bytes = io.BytesIO()
    image.save(bytes, format='PNG')
    window['trim'].update(data=bytes.getvalue())

def update_image(name, image):
    bytes = io.BytesIO()
    image.save(bytes, format='PNG')
    window[name].update(data=bytes.getvalue())

def feedback():
    window['starting'].update(window['recog_starting'].get())
    window['trigger'].update(window['recog_trigger'].visible)
    window['cutin_mission'].update(window['recog_cutin_mission'].visible)
    window['cutin_bit'].update(window['recog_cutin_bit'].visible)
    window['rival'].update(window['recog_rival'].visible)
    play_side = window['recog_play_side'].get()
    if play_side == '':
        window['play_side_none'].update(True)
    if play_side == '1P':
        window['play_side_1p'].update(True)
    if play_side == '2P':
        window['play_side_2p'].update(True)

def set_labels(label):
    window['starting'].update('')
    window['trigger'].update(True)
    window['cutin_mission'].update(False)
    window['cutin_bit'].update(False)
    window['rival'].update(False)
    window['play_side_none'].update(True)
    if not label is None:
        if 'starting' in label.keys():
            window['starting'].update(label['starting'])
        if 'trigger' in label.keys():
            window['trigger'].update(label['trigger'])
        if 'cutin_mission' in label.keys():
            window['cutin_mission'].update(label['cutin_mission'])
        if 'cutin_bit' in label.keys():
            window['cutin_bit'].update(label['cutin_bit'])
        if 'rival' in label.keys():
            window['rival'].update(label['rival'])
        if 'play_side' in label.keys():
            if label['play_side'] == '1P':
                window['play_side_1p'].update(True)
            if label['play_side'] == '2P':
                window['play_side_2p'].update(True)

def set_recognition(screen):
    starting = recog.get_starting(screen.image)
    trigger = recog.search_trigger(screen.image)
    cutin_mission = recog.search_cutin_mission(screen.image)
    cutin_bit = recog.search_cutin_bit(screen.image)
    rival = recog.search_rival(screen.image)
    play_side = recog.get_play_side(screen.image)

    window['recog_starting'].update(starting if starting is not None else '')
    window['recog_trigger'].update(visible=trigger)
    window['recog_cutin_mission'].update(visible=cutin_mission)
    window['recog_cutin_bit'].update(visible=cutin_bit)
    window['recog_rival'].update(visible=rival)
    window['recog_play_side'].update(play_side if play_side is not None else '')
