import PySimpleGUI as sg
import io

from define import define
from recog import recog,informations_trimsize,details_trimsize
from .static import title,icon_path,background_color

in_area_background_color='#5779dd'

def layout_manage(keys):
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
    selectable_value_list['delimita'] = ['', ',', '/']

    result_informations = [
        [
            sg.Text('プレイモード', size=(18, 1)),
            sg.Text(key='result_play_mode', background_color=in_area_background_color)
        ],
        [
            sg.Text('難易度', size=(18, 1)),
            sg.Text(key='result_difficulty', background_color=in_area_background_color),
            sg.Text(key='result_level', background_color=in_area_background_color)
        ],
        [
            sg.Text('曲名', size=(18, 1)),
            sg.Text(key='result_music', background_color=in_area_background_color)
        ]
    ]

    result_details = [
        [
            sg.Text('配置オプション', size=(21, 1)),
            sg.Text(key='result_option_arrange', background_color=in_area_background_color)
        ],
        [
            sg.Text('FLIPオプション', size=(21, 1)),
            sg.Text(key='result_option_flip', background_color=in_area_background_color)
        ],
        [
            sg.Text('アシストオプション', size=(21, 1)),
            sg.Text(key='result_option_assist', background_color=in_area_background_color)
        ],
        [
            sg.Text('特殊オプション', size=(21, 1)),
            sg.Text('BATTLE', visible=False, key='result_option_battle', background_color=in_area_background_color),
            sg.Text('H-RANDOM', visible=False, key='result_option_h-random', background_color=in_area_background_color)
        ],
        [
            sg.Text('クリアタイプ', size=(21, 1)),
            sg.Text(key='result_clear_type', size=(10, 1), background_color=in_area_background_color),
            sg.Text('NEW', visible=False, key='result_clear_type_new', background_color=in_area_background_color)
        ],
        [
            sg.Text('DJレベル', size=(21, 1)),
            sg.Text(key='result_dj_level', size=(10, 1), background_color=in_area_background_color),
            sg.Text('NEW', visible=False, key='result_dj_level_new', background_color=in_area_background_color)
        ],
        [
            sg.Text('スコア', size=(21, 1)),
            sg.Text(key='result_score', size=(10, 1), background_color=in_area_background_color),
            sg.Text('NEW', visible=False, key='result_score_new', background_color=in_area_background_color)
        ],
        [
            sg.Text('ミスカウント', size=(21, 1)),
            sg.Text(key='result_miss_count', size=(10, 1), background_color=in_area_background_color),
            sg.Text('NEW', visible=False, key='result_miss_count_new', background_color=in_area_background_color)
        ]
    ]

    manage_label_define = [
        [
            sg.Text('プレイモード', size=(15, 1)),
            sg.Combo(selectable_value_list['play_modes'], key='play_mode', readonly=True, enable_events=True)
        ],
        [
            sg.Text('難易度', size=(15, 1)),
            sg.Combo(selectable_value_list['difficulties'], key='difficulty', size=(13, 1), readonly=True),
            sg.Combo(selectable_value_list['levels'], key='level', readonly=True)
        ],
        [
            sg.Text('曲名', size=(15, 1)),
            sg.Input(key='music', size=(30, 1)),
        ],
        [
            sg.Text('オプション', size=(15, 1)),
            sg.Column([
                [
                    sg.Text('SP配置', size=(11, 1)),
                    sg.Combo(selectable_value_list['options_arrange'], key='option_arrange', size=(10, 1), readonly=True)
                ],
                [
                    sg.Text('DP配置', size=(11, 1)),
                    sg.Combo(selectable_value_list['options_arrange_dp'], key='option_arrange_1p', size=(6, 1), readonly=True),
                    sg.Text('/', background_color=in_area_background_color,pad=0),
                    sg.Combo(selectable_value_list['options_arrange_dp'], key='option_arrange_2p', size=(6, 1), readonly=True)
                ],
                [
                    sg.Text('BATTLE配置', size=(11, 1)),
                    sg.Combo(selectable_value_list['options_arrange_sync'], key='option_arrange_sync', size=(10, 1), readonly=True)
                ],
                [
                    sg.Text('フリップ', size=(11, 1)),
                    sg.Combo(selectable_value_list['options_flip'], key='option_flip', size=(10, 1), readonly=True)
                ],
                [
                    sg.Text('アシスト', size=(11, 1)),
                    sg.Combo(selectable_value_list['options_assist'], key='option_assist', size=(8, 1), readonly=True)
                ]
            ], background_color=in_area_background_color, pad=0)
        ],
        [
            sg.Text('特殊オプション', size=(15, 1)),
            sg.Check('BATTLE', key='option_battle', background_color=in_area_background_color),
            sg.Check('H-RANDOM', key='option_h-random', background_color=in_area_background_color)
        ],
        [
            sg.Text('クリアタイプ', size=(15, 1)),
            sg.Combo(selectable_value_list['clear_types'], key='clear_type', size=(11, 1), readonly=True),
            sg.Checkbox('NEW', key='clear_type_new', background_color=in_area_background_color)
        ],
        [
            sg.Text('DJレベル', size=(15, 1)),
            sg.Combo(selectable_value_list['dj_levels'], key='dj_level', size=(11, 1), readonly=True),
            sg.Checkbox('NEW', key='dj_level_new', background_color=in_area_background_color)
        ],
        [
            sg.Text('スコア', size=(15, 1)),
            sg.Input(key='score', size=(12, 1)),
            sg.Checkbox('NEW', key='score_new', background_color=in_area_background_color)
        ],
        [
            sg.Text('ミスカウント', size=(15, 1)),
            sg.Input(key='miss_count', size=(12, 1)),
            sg.Checkbox('NEW', key='miss_count_new', background_color=in_area_background_color)
        ],
        [
            sg.Button('アノテーション保存', key='button_label_overwrite'),
            sg.Button('認識結果から引用', key='button_recog')
        ],
        [
            sg.Checkbox('曲名なしのみ', key='only_undefined_music', enable_events=True, background_color=in_area_background_color)
        ]
    ]

    return [
        [
            sg.Column([
                [
                    sg.Column([
                        [sg.Image(key='image_informations', size=informations_trimsize, background_color=background_color)],
                        [sg.Image(key='image_details', size=details_trimsize, background_color=background_color)]
                    ], background_color=background_color),
                    sg.Listbox(keys, key='list_keys', size=(20, 20), enable_events=True),
                ],
                [
                    sg.Column(result_informations, size=(300, 210), background_color=in_area_background_color),
                    sg.Column(result_details, size=(325, 210), background_color=in_area_background_color)
                ],
            ], pad=0, background_color=background_color),
            sg.Column([
                [sg.Column(manage_label_define, size=(390,560), background_color=in_area_background_color)],
            ], pad=0, background_color=background_color)
        ]
    ]

def generate_window(keys):
    global window

    window = sg.Window(
        title,
        layout_manage(keys),
        icon=icon_path,
        grab_anywhere=True,
        return_keyboard_events=True,
        resizable=False,
        finalize=True,
        enable_close_attempted_event=True,
        background_color=background_color
    )

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

def display_informations(image):
    if image is not None:
        bytes = io.BytesIO()
        image.save(bytes, format='PNG')
        window['image_informations'].update(data=bytes.getvalue(),visible=True)
    else:
        window['image_informations'].update(visible=False)

def display_details(image):
    if image is not None:
        bytes = io.BytesIO()
        image.save(bytes, format='PNG')
        window['image_details'].update(data=bytes.getvalue(),visible=True)
    else:
        window['image_details'].update(visible=False)

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

def reset_informations():
    window['result_play_mode'].update('')
    window['result_difficulty'].update('')
    window['result_level'].update('')
    window['result_music'].update('')

def set_informations(image):
    play_mode, difficulty, level, music = recog.get_informations(image)

    window['result_play_mode'].update(play_mode if play_mode is not None else '')
    window['result_difficulty'].update(difficulty if difficulty is not None else '')
    window['result_level'].update(level if level is not None else '')
    window['result_music'].update(music if music is not None else '')

def reset_details():
    window['result_option_arrange'].update('')
    window['result_option_flip'].update('')
    window['result_option_assist'].update('')
    window['result_option_battle'].update(visible=False)
    window['result_option_h-random'].update(visible=False)
    window['result_clear_type'].update('')
    window['result_dj_level'].update('')
    window['result_score'].update('')
    window['result_miss_count'].update('')
    window['result_clear_type_new'].update(visible=False)
    window['result_dj_level_new'].update(visible=False)
    window['result_score_new'].update(visible=False)
    window['result_miss_count_new'].update(visible=False)

def set_details(image):
    option, clear_type, dj_level, score, miss_count, clear_type_new, dj_level_new, score_new, miss_count_new = recog.get_details(image)

    window['result_option_arrange'].update(option['arrange'] if option['arrange'] is not None else '')
    window['result_option_flip'].update(option['flip'] if option['flip'] is not None else '')
    window['result_option_assist'].update(option['assist'] if option['assist'] is not None else '')
    window['result_option_battle'].update(visible=option['battle'])
    window['result_option_h-random'].update(visible=option['h-random'])
    window['result_clear_type'].update(clear_type if clear_type is not None else '')
    window['result_dj_level'].update(dj_level if dj_level is not None else '')
    window['result_score'].update(score if score is not None else '')
    window['result_miss_count'].update(miss_count if miss_count is not None else '')
    window['result_clear_type_new'].update(visible=clear_type_new)
    window['result_dj_level_new'].update(visible=dj_level_new)
    window['result_score_new'].update(visible=score_new)
    window['result_miss_count_new'].update(visible=miss_count_new)

def set_result():
    window['play_mode'].update(window['result_play_mode'].get())
    window['difficulty'].update(window['result_difficulty'].get())
    window['level'].update(window['result_level'].get())
    window['music'].update(window['result_music'].get())

    window['option_arrange'].update('')
    window['option_arrange_1p'].update('')
    window['option_arrange_2p'].update('')
    window['option_arrange_sync'].update('')
    if window['result_option_arrange'].get() in define.value_list['options_arrange']:
        window['option_arrange'].update(window['result_option_arrange'].get())
    if '/' in window['result_option_arrange'].get():
        left, right = window['result_option_arrange'].get().split('/')
        window['option_arrange_1p'].update(left)
        window['option_arrange_2p'].update(right)
    if window['result_option_arrange'].get() in define.value_list['options_arrange_sync']:
        window['option_arrange_sync'].update(window['result_option_arrange'].get())

    window['option_flip'].update(window['result_option_flip'].get())
    window['option_assist'].update(window['result_option_assist'].get())
    window['option_battle'].update(window['result_option_battle'].visible)
    window['option_h-random'].update(window['result_option_h-random'].visible)
    window['clear_type'].update(window['result_clear_type'].get())
    window['dj_level'].update(window['result_dj_level'].get())
    window['score'].update(window['result_score'].get())
    window['miss_count'].update(window['result_miss_count'].get())
    window['clear_type_new'].update(window['result_clear_type_new'].visible)
    window['dj_level_new'].update(window['result_dj_level_new'].visible)
    window['score_new'].update(window['result_score_new'].visible)
    window['miss_count_new'].update(window['result_miss_count_new'].visible)

    window['music'].set_focus()

def set_labels(label):
    window['play_mode'].update('')
    window['difficulty'].update('')
    window['level'].update('')
    window['option_arrange'].update('')
    window['option_arrange_1p'].update('')
    window['option_arrange_2p'].update('')
    window['option_arrange_sync'].update('')
    window['option_flip'].update('')
    window['option_assist'].update('')
    window['option_battle'].update(False)
    window['option_h-random'].update(False)
    window['clear_type'].update('')
    window['clear_type_new'].update('')
    window['dj_level'].update('')
    window['dj_level_new'].update('')
    window['score'].update('')
    window['score_new'].update('')
    window['miss_count'].update('')
    window['miss_count_new'].update('')
    window['music'].update('')
    if not label is None:
        if 'play_mode' in label.keys():
            window['play_mode'].update(label['play_mode'])
        if 'difficulty' in label.keys():
            window['difficulty'].update(label['difficulty'])
        if 'level' in label.keys():
            window['level'].update(label['level'])
        if 'music' in label.keys():
            window['music'].update(label['music'])
        if 'option_battle' in label.keys():
            window['option_battle'].update(label['option_battle'])
        if 'option_arrange' in label.keys():
            window['option_arrange'].update(label['option_arrange'])
        if 'option_arrange_dp' in label.keys():
            left, right = label['option_arrange_dp'].split('/')
            window['option_arrange_1p'].update(left)
            window['option_arrange_2p'].update(right)
        if 'option_arrange_sync' in label.keys():
            window['option_arrange_sync'].update(label['option_arrange_sync'])
        if 'option_flip' in label.keys():
            window['option_flip'].update(label['option_flip'])
        if 'option_assist' in label.keys():
            window['option_assist'].update(label['option_assist'])
        if 'option_battle' in label.keys():
            window['option_battle'].update(label['option_battle'])
        if 'option_h-random' in label.keys():
            window['option_h-random'].update(label['option_h-random'])
        if 'clear_type' in label.keys():
            window['clear_type'].update(label['clear_type'])
        if 'clear_type_new' in label.keys():
            window['clear_type_new'].update(label['clear_type_new'])
        if 'dj_level' in label.keys():
            window['dj_level'].update(label['dj_level'])
        if 'dj_level_new' in label.keys():
            window['dj_level_new'].update(label['dj_level_new'])
        if 'score' in label.keys():
            window['score'].update(label['score'])
        if 'score_new' in label.keys():
            window['score_new'].update(label['score_new'])
        if 'miss_count' in label.keys():
            window['miss_count'].update(label['miss_count'])
        if 'miss_count_new' in label.keys():
            window['miss_count_new'].update(label['miss_count_new'])
