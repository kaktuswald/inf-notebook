import PySimpleGUI as sg
import io
import numpy as np

from define import define
from recog import Recognition as recog
from .static import title,icon_path,background_color

imagescale = 1 / 2
imagesize = list((np.array([696, 546],dtype=np.int32) * imagescale).astype(np.int32))
in_area_background_color='#5779dd'

def layout_manage(keys):
    selectable_value_list = {}
    for key, values in define.value_list.items():
        selectable_value_list[key] = ['', *values]
    selectable_value_list['versions'] = [
        '',
        '1st',
        'substream',
        '2nd style',
        '3rd style',
        '4th style',
        '5th style',
        '6th style',
        '7th style',
        '8th style',
        '9th style',
        '10th style',
        'IIDX RED',
        'HAPPY SKY',
        'DistorteD',
        'GOLD',
        'DJ TROOPERS',
        'EMPRESS',
        'SIRIUS',
        'Resort Anthem',
        'Lincle',
        'tricoro',
        'SPADA',
        'PENDUAL',
        'copula',
        'SINOBUZ',
        'CANNON BALLERS',
        'Rootage',
        'HEROIC VERSE',
        'BISTROVER',
        'CastHour',
        'RESIDENT',
        'INFINITAS'
    ]
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
            sg.Text('バージョン', size=(15, 1)),
            sg.Text(key='result_version', background_color=in_area_background_color)
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
            sg.Text('バージョン', size=(18, 1)),
            sg.Combo(selectable_value_list['versions'], key='version', size=(18, 1), readonly=True, enable_events=True)
        ],
        [
            sg.Text('曲名の種別', size=(18, 1)),
            sg.Combo(selectable_value_list['musictypes'], key='musictype', size=(16, 1), readonly=True, enable_events=True)
        ],
        [
            sg.Text('曲名', size=(18, 1)),
            sg.Input(key='musicname', size=(30, 1)),
        ],
        [
            sg.Text('選択難易度', size=(18, 1)),
            sg.Combo(selectable_value_list['difficulties'], key='difficulty', size=(14, 1), readonly=True)
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
        [sg.Checkbox('バージョンなしのみ', key='only_undefined_version', enable_events=True, background_color=in_area_background_color)],
        [sg.Input(key='keyfilter', enable_events=True)]
    ]

    return [
        [
            sg.Column([
                [
                    sg.Image(key='image', size=imagesize, background_color=background_color),
                    sg.Listbox(keys, key='list_keys', size=(24, 19), enable_events=True),
                ],
                [
                    sg.Column(results1, size=(200, 215), background_color=in_area_background_color),
                    sg.Column(results2, size=(340, 215), background_color=in_area_background_color),
                ],
            ], pad=0, background_color=background_color),
            sg.Column([
                [sg.Column(manage_label_define, size=(385,540), background_color=in_area_background_color)],
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
    window['result_version'].update('')
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

from resources import resource

def recognize(image):
    if resource.musicselect is None:
        return
    
    playmode = recog.MusicSelect.get_playmode(image)
    version = recog.MusicSelect.get_version(image)
    musicname = recog.MusicSelect.get_musicname(image)
    difficulty = recog.MusicSelect.get_difficulty(image)
    cleartype = recog.MusicSelect.get_cleartype(image)
    djlevel = recog.MusicSelect.get_djlevel(image)
    score = recog.MusicSelect.get_score(image)
    misscount = recog.MusicSelect.get_misscount(image)
    levels = recog.MusicSelect.get_levels(image)

    window['result_playmode'].update(playmode if playmode is not None else '')
    window['result_version'].update(version if version is not None else '')
    window['result_musicname'].update(musicname if musicname is not None else '')
    window['result_difficulty'].update(difficulty if difficulty is not None else '')
    window['result_cleartype'].update(cleartype if cleartype is not None else '')
    window['result_djlevel'].update(djlevel if djlevel is not None else '')
    window['result_score'].update(score if score is not None else '')
    window['result_misscount'].update(misscount if misscount is not None else '')
    window['result_level_beginner'].update(levels['BEGINNER'] if 'BEGINNER' in levels.keys() else '')
    window['result_level_normal'].update(levels['NORMAL'] if 'NORMAL' in levels.keys() else '')
    window['result_level_hyper'].update(levels['HYPER'] if 'HYPER' in levels.keys() else '')
    window['result_level_another'].update(levels['ANOTHER'] if 'ANOTHER' in levels.keys() else '')
    window['result_level_leggendaria'].update(levels['LEGGENDARIA'] if 'LEGGENDARIA' in levels.keys() else '')

def reflect_recognized():
    window['level_beginner'].update(window['result_level_beginner'].get())
    window['level_normal'].update(window['result_level_normal'].get())
    window['level_hyper'].update(window['result_level_hyper'].get())
    window['level_another'].update(window['result_level_another'].get())
    window['level_leggendaria'].update(window['result_level_leggendaria'].get())

    window['playmode'].update(window['result_playmode'].get())
    window['version'].update(window['result_version'].get())
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
    window['version'].update('')
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
    window['version'].update(label['version'] if 'version' in label.keys() else '')
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
        keys = [key for key in keys if key in labels.keys() and (not 'musicname' in labels[key].keys() or labels[key]['musicname'] == '')]
    if window['only_undefined_version'].get():
        keys = [key for key in keys if key in labels.keys() and (not 'version' in labels[key].keys() or labels[key]['version'] == '')]
    if len(window['keyfilter'].get()) > 0:
        keys = [key for key in keys if window['keyfilter'].get() in key]
    window['list_keys'].update(keys)
