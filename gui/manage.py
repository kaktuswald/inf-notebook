import PySimpleGUI as sg
import io
from PIL import Image

from define import define
from .static import title,icon_path,background_color,in_area_background_color

default_box = (0, 0, 1920, 1080)
scales = ['1/1', '1/2', '1/4']

def layout_manage(filenames):
    selectable_value_list = {}
    for key, values in define.value_list.items():
        selectable_value_list[key] = ['', *values]
    selectable_value_list['all_options'] = [
        '',
        *define.value_list['options_arrange'],
        *define.value_list['options_arrange_dp'],
        *define.value_list['options_arrange_sync'],
        *define.value_list['options_flip'],
        *define.value_list['options_assist'],
        'BATTLE',
        'H-RANDOM'
    ]

    manage_screen = [
        [sg.Text('画面', size=(20, 1))],
        [sg.Radio('なし', key='screen_none', group_id='screen', background_color=in_area_background_color)],
        [sg.Radio('ローディング', key='screen_loading', group_id='screen', background_color=in_area_background_color)],
        [sg.Radio('選曲', key='screen_music_select', group_id='screen', background_color=in_area_background_color)],
        [sg.Radio('プレイ中', key='screen_playing', group_id='screen', background_color=in_area_background_color)],
        [sg.Radio('リザルト', key='screen_result', group_id='screen', background_color=in_area_background_color, default=True)]
    ]

    manage_label = [
        [
            sg.Text('リザルト限定', size=(16, 1)),
            sg.Checkbox('保存可能', key='is_savable', default=True, background_color=in_area_background_color)
        ],
        [
            sg.Text('ライバル挑戦状', size=(16, 1)),
            sg.Checkbox('表示あり', key='rival', default=False, background_color=in_area_background_color)
        ],
        [
            sg.Text('グラフ', size=(16, 1)),
            sg.Radio('ゲージ', key='graph_gauge', group_id='graph', background_color=in_area_background_color),
            sg.Radio('レーン', key='graph_lanes', group_id='graph', background_color=in_area_background_color),
            sg.Radio('小節', key='graph_measures', group_id='graph', background_color=in_area_background_color),
        ],
        [
            sg.Text('リザルト', size=(16, 1)),
            sg.Text('モード', background_color=in_area_background_color),
            sg.Combo(['', 'SP', 'DP'], key='play_mode'),
            sg.Text('サイド', background_color=in_area_background_color),
            sg.Combo(['', '1P', '2P'], key='play_side')
        ],
        [
            sg.Text('途中落ち', size=(16, 1)),
            sg.Checkbox('表示あり', key='dead', default=False, background_color=in_area_background_color)
        ],
        [
            sg.Button('アノテーション保存', key='button_label_overwrite')
        ]
    ]
    return [
        [
            sg.Column([
                [
                    sg.Column([
                        [
                            sg.Text('画像表示スケール', background_color=background_color),
                            sg.Combo(scales, default_value='1/3', readonly=True, key='scale')
                        ],
                        [sg.Image(key='screenshot', size=(640, 360), background_color=background_color)]
                    ], pad=0, background_color=background_color),
                    sg.Listbox(filenames, key='list_screens', size=(27, 21), enable_events=True),
                    sg.Column([
                        [sg.Radio('すべて', default=True, key='search_all', group_id='search', enable_events=True, background_color=background_color)],
                        [sg.Radio('選曲のみ', key='search_only_music_select', group_id='search', enable_events=True, background_color=background_color)],
                        [sg.Radio('プレイ中のみ', key='search_only_playing', group_id='search', enable_events=True, background_color=background_color)],
                        [sg.Radio('リザルトのみ', key='search_only_result', group_id='search', enable_events=True, background_color=background_color)],
                        [sg.Radio('アノテーションなし', key='search_only_no_annotation', group_id='search', enable_events=True, background_color=background_color)]
                    ], pad=0, background_color=background_color)
                ],
                [
                    sg.Column(manage_screen, size=(190, 180), background_color=in_area_background_color),
                    sg.Column(manage_label, size=(400, 180), background_color=in_area_background_color),
                ],
            ], pad=0, background_color=background_color)
        ],
    ]

def generate_window(filenames):
    global window

    window = sg.Window(
        title,
        layout_manage(filenames),
        icon=icon_path,
        return_keyboard_events=True,
        resizable=False,
        finalize=True,
        enable_close_attempted_event=True,
        background_color=background_color
    )

    return window

def display_image(image):
    scale = window['scale'].get()
    if scale == '1/2':
        image = image.resize((image.width // 2, image.height // 2))
    if scale == '1/3':
        image = image.resize((image.width // 3, image.height // 3))
    if scale == '1/4':
        image = image.resize((image.width // 4, image.height // 4))
    
    bytes = io.BytesIO()
    image.save(bytes, format='PNG')
    imagevalue = bytes.getvalue()
    bytes.close()

    window['screenshot'].update(size=image.size, data=imagevalue)

def set_labels(label):
    window['screen_none'].update(True)
    window['is_savable'].update(False)
    window['rival'].update(False)
    window['play_side'].update('')
    window['play_mode'].update('')
    window['dead'].update(False)
    window['graph_gauge'].update(False)
    window['graph_lanes'].update(False)
    window['graph_measures'].update(False)
    if not label is None:
        if 'screen' in label.keys():
            window[f"screen_{label['screen']}"].update(True)
        if 'is_savable' in label.keys():
            window['is_savable'].update(label['is_savable'])
        if 'rival' in label.keys():
            window['rival'].update(label['rival'])
        if 'graphtype' in label.keys() and label['graphtype'] is not None:
            window[f"graph_{label['graphtype']}"].update(True)
        if 'play_side' in label.keys():
            window['play_side'].update(label['play_side'])
        if 'play_mode' in label.keys():
            window['play_mode'].update(label['play_mode'])
        if 'dead' in label.keys():
            window['dead'].update(label['dead'])
