import PySimpleGUI as sg
import io
import numpy as np

from define import define
from recog import Recognition as recog
from .static import title,icon_path,background_color

imagescale = 1 / 2
imagesize = list((np.array([1280, 720],dtype=np.int32) * imagescale).astype(np.int32))
in_area_background_color='#5779dd'

def layout_manage(keys):
    selectable_value_list = {}
    for key, values in define.value_list.items():
        selectable_value_list[key] = ['', *values]
    selectable_value_list['musictypes'] = ['', 'ARCADE', 'INFINITAS', 'LEGGENDARIA']

    results1 = [
        [
            sg.Text('ビギナーレベル', size=(18, 1)),
            sg.Text(key='result_level_beginner', background_color=in_area_background_color),
        ],
        [
            sg.Text('ノーマルレベル', size=(18, 1)),
            sg.Text(key='result_level_normal', background_color=in_area_background_color),
        ],
        [
            sg.Text('ハイパーレベル', size=(18, 1)),
            sg.Text(key='result_level_hyper', background_color=in_area_background_color),
        ],
        [
            sg.Text('アナザーレベル', size=(18, 1)),
            sg.Text(key='result_level_another', background_color=in_area_background_color),
        ],
        [
            sg.Text('レジェンダリアレベル', size=(18, 1)),
            sg.Text(key='result_level_leggendaria', background_color=in_area_background_color),
        ]
    ]
    results2 = [
        [
            sg.Text('プレイモード', size=(15, 1)),
            sg.Text(key='result_playmode', background_color=in_area_background_color)
        ],
        [
            sg.Text('曲名', size=(15, 1)),
            sg.Text(key='result_musicname', background_color=in_area_background_color)
        ],
        [
            sg.Text('選択難易度', size=(15, 1)),
            sg.Text(key='result_difficulty', background_color=in_area_background_color),
        ],
        [
            sg.Text('クリアタイプ', size=(15, 1)),
            sg.Text(key='result_cleartype', size=(10, 1), background_color=in_area_background_color),
        ],
        [
            sg.Text('DJレベル', size=(15, 1)),
            sg.Text(key='result_djlevel', size=(10, 1), background_color=in_area_background_color),
        ],
        [
            sg.Text('スコア', size=(15, 1)),
            sg.Text(key='result_score', size=(10, 1), background_color=in_area_background_color),
        ],
        [
            sg.Text('ミスカウント', size=(15, 1)),
            sg.Text(key='result_misscount', size=(10, 1), background_color=in_area_background_color),
        ]
    ]

    manage_label_define = [
        [
            sg.Text('プレイモード', size=(18, 1)),
            sg.Combo(selectable_value_list['play_modes'], key='playmode', readonly=True, enable_events=True)
        ],
        [
            sg.Text('曲名の種別', size=(18, 1)),
            sg.Combo(selectable_value_list['musictypes'], key='musictype', readonly=True, enable_events=True)
        ],
        [
            sg.Text('曲名', size=(18, 1)),
            sg.Input(key='musicname', size=(30, 1)),
        ],
        [
            sg.Text('選択難易度', size=(18, 1)),
            sg.Combo(selectable_value_list['difficulties'], key='difficulty', size=(13, 1), readonly=True)
        ],
        [
            sg.Text('クリアタイプ', size=(18, 1)),
            sg.Combo(selectable_value_list['clear_types'], key='cleartype', size=(11, 1), readonly=True),
        ],
        [
            sg.Text('DJレベル', size=(18, 1)),
            sg.Combo(selectable_value_list['dj_levels'], key='djlevel', size=(11, 1), readonly=True),
        ],
        [
            sg.Text('スコア', size=(18, 1)),
            sg.Input(key='score', size=(12, 1)),
        ],
        [
            sg.Text('ミスカウント', size=(18, 1)),
            sg.Input(key='misscount', size=(12, 1)),
        ],
        [
            sg.Text('ビギナーレベル', size=(18, 1)),
            sg.Combo(selectable_value_list['levels'], key='level_beginner', readonly=True)
        ],
        [
            sg.Text('ノーマルレベル', size=(18, 1)),
            sg.Combo(selectable_value_list['levels'], key='level_normal', readonly=True)
        ],
        [
            sg.Text('ハイパーレベル', size=(18, 1)),
            sg.Combo(selectable_value_list['levels'], key='level_hyper', readonly=True)
        ],
        [
            sg.Text('アナザーレベル', size=(18, 1)),
            sg.Combo(selectable_value_list['levels'], key='level_another', readonly=True)
        ],
        [
            sg.Text('レジェンダリアレベル', size=(18, 1)),
            sg.Combo(selectable_value_list['levels'], key='level_leggendaria', readonly=True)
        ],
        [
            sg.Button('アノテーション保存', key='button_label_overwrite'),
            sg.Button('認識結果から引用', key='button_recog')
        ],
        [sg.Checkbox('未アノテーションのみ', key='only_not_annotation', enable_events=True, background_color=in_area_background_color)],
        [sg.Checkbox('曲名なしのみ', key='only_undefined_musicname', enable_events=True, background_color=in_area_background_color)],
        [sg.Checkbox('F-COMBOのみ', key='only_full_combo', enable_events=True, background_color=in_area_background_color)],
        [sg.Input(key='keyfilter', enable_events=True)]
    ]

    return [
        [
            sg.Column([
                [
                    sg.Image(key='image', size=imagesize, background_color=background_color),
                    sg.Listbox(keys, key='list_keys', size=(24, 22), enable_events=True),
                ],
                [
                    sg.Column(results1, size=(300, 190), background_color=in_area_background_color),
                    sg.Column(results2, size=(500, 190), background_color=in_area_background_color),
                ],
            ], pad=0, background_color=background_color),
            sg.Column([
                [sg.Column(manage_label_define, size=(385,580), background_color=in_area_background_color)],
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

def display_image(image):
    if image is not None:
        bytes = io.BytesIO()
        image.save(bytes, format='PNG')
        window['image'].update(data=bytes.getvalue(),visible=True,size=imagesize,)
    else:
        window['image'].update(visible=False)

def clear_results():
    window['result_playmode'].update('')
    window['result_musicname'].update('')
    window['result_difficulty'].update('')
    window['result_cleartype'].update('')
    window['result_djlevel'].update('')
    window['result_score'].update('')
    window['result_misscount'].update('')
    window['result_level_beginner'].update('')
    window['result_level_normal'].update('')
    window['result_level_hyper'].update('')
    window['result_level_another'].update('')
    window['result_level_leggendaria'].update('')

def recognize(image):
    playmode = recog.MusicSelect.get_playmode(image)
    musicname = recog.MusicSelect.get_musicname(image)
    difficulty = recog.MusicSelect.get_difficulty(image)
    cleartype = recog.MusicSelect.get_cleartype(image)
    djlevel = recog.MusicSelect.get_djlevel(image)
    score = recog.MusicSelect.get_score(image)
    misscount = recog.MusicSelect.get_misscount(image)
    levels = recog.MusicSelect.get_levels(image)

    window['result_playmode'].update(playmode if playmode is not None else '')
    window['result_musicname'].update(musicname if musicname is not None else '')
    window['result_difficulty'].update(difficulty if difficulty is not None else '')
    window['result_cleartype'].update(cleartype if cleartype is not None else '')
    window['result_djlevel'].update(djlevel if djlevel is not None else '')
    window['result_score'].update(score if score is not None else '')
    window['result_misscount'].update(misscount if misscount is not None else '')
    window['result_level_beginner'].update(levels['beginner'] if 'beginner' in levels.keys() else '')
    window['result_level_normal'].update(levels['normal'] if 'normal' in levels.keys() else '')
    window['result_level_hyper'].update(levels['hyper'] if 'hyper' in levels.keys() else '')
    window['result_level_another'].update(levels['another'] if 'another' in levels.keys() else '')
    window['result_level_leggendaria'].update(levels['leggendaria'] if 'leggendaria' in levels.keys() else '')

def reflect_recognized():
    window['level_beginner'].update(window['result_level_beginner'].get())
    window['level_normal'].update(window['result_level_normal'].get())
    window['level_hyper'].update(window['result_level_hyper'].get())
    window['level_another'].update(window['result_level_another'].get())
    window['level_leggendaria'].update(window['result_level_leggendaria'].get())

    window['playmode'].update(window['result_playmode'].get())
    window['musictype'].update('ARCADE')
    window['musicname'].update(window['result_musicname'].get())
    window['difficulty'].update(window['result_difficulty'].get())
    window['cleartype'].update(window['result_cleartype'].get())
    window['djlevel'].update(window['result_djlevel'].get())
    window['score'].update(window['result_score'].get())
    window['misscount'].update(window['result_misscount'].get())

    window['musicname'].set_focus()

def clear_labels():
    window['playmode'].update('')
    window['musictype'].update('')
    window['musicname'].update('')
    window['difficulty'].update('')
    window['cleartype'].update('')
    window['djlevel'].update('')
    window['score'].update('')
    window['misscount'].update('')
    window['level_beginner'].update('')
    window['level_normal'].update('')
    window['level_hyper'].update('')
    window['level_another'].update('')
    window['level_leggendaria'].update('')

def set_labels(label):
    window['playmode'].update(label['playmode'])
    window['musictype'].update(label['musictype'] if 'musictype' in label.keys() else '')
    window['musicname'].update(label['musicname'])
    window['difficulty'].update(label['difficulty'])
    window['cleartype'].update(label['cleartype'])
    window['djlevel'].update(label['djlevel'])
    window['score'].update(label['score'])
    window['misscount'].update(label['misscount'])
    window['level_beginner'].update(label['level_beginner'])
    window['level_normal'].update(label['level_normal'])
    window['level_hyper'].update(label['level_hyper'])
    window['level_another'].update(label['level_another'])
    window['level_leggendaria'].update(label['level_leggendaria'])

def change_search_condition(keys, labels):
    if window['only_not_annotation'].get():
        keys = [key for key in keys if not key in labels.keys()]
    if window['only_undefined_musicname'].get():
        keys = [key for key in keys if key in labels.keys() and labels[key]['informations'] is not None and labels[key]['informations']['musicname'] == '']
    if window['only_full_combo'].get():
        keys = [key for key in keys if key in labels.keys() and labels[key]['details'] is not None and (('cleartype_best' in labels[key]['details'].keys() and labels[key]['details']['cleartype_best'] == 'F-COMBO') or labels[key]['details']['cleartype_current'] == 'F-COMBO')]
    if len(window['keyfilter'].get()) > 0:
        keys = [key for key in keys if window['keyfilter'].get() in key]
    window['list_keys'].update(keys)
