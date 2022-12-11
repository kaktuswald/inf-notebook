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

    for key in ['trigger', 'cutin_mission', 'cutin_bit']:
        image = Image.fromarray(masks[key].value)
        bytes = io.BytesIO()
        image.save(bytes, format='PNG')
        images[key] = bytes.getvalue()

    result = [
        [
            sg.Text('ライバル挑戦状', size=(22, 1)),
            sg.Text('あり', visible=False, key='result_rival', background_color='#7799fd', text_color='#000000')
        ],
        [
            sg.Text('プレイモード', size=(22, 1)),
            sg.Text(key='result_play_mode', background_color='#7799fd', text_color='#000000')
        ],
        [
            sg.Text('難易度', size=(22, 1)),
            sg.Text(key='result_difficulty', background_color='#7799fd', text_color='#000000'),
            sg.Text(key='result_level', background_color='#7799fd', text_color='#000000')
        ],
        [
            sg.Text('曲名', size=(22, 1)),
            sg.Text(key='result_music', background_color='#7799fd', text_color='#000000')
        ],
        [
            sg.Text('プレイサイド', size=(22, 1)),
            sg.Text(key='result_play_side', background_color='#7799fd', text_color='#000000')
        ],
        [
            sg.Text('オプション', size=(22, 1)),
            sg.Text('あり', visible=False, key='result_use_option', background_color='#7799fd', text_color='#000000')
        ],
        [
            sg.Text('配置オプション', size=(22, 1)),
            sg.Text(key='result_option_arrange', background_color='#7799fd', text_color='#000000')
        ],
        [
            sg.Text('FLIPオプション', size=(22, 1)),
            sg.Text(key='result_option_flip', background_color='#7799fd', text_color='#000000')
        ],
        [
            sg.Text('アシストオプション', size=(22, 1)),
            sg.Text(key='result_option_assist', background_color='#7799fd', text_color='#000000')
        ],
        [
            sg.Text('特殊オプション', size=(22, 1)),
            sg.Text('BATTLE', visible=False, key='result_option_battle', background_color='#7799fd', text_color='#000000'),
            sg.Text('H-RANDOM', visible=False, key='result_option_h-random', background_color='#7799fd', text_color='#000000')
        ],
        [
            sg.Text('クリアタイプ', size=(22, 1)),
            sg.Text(key='result_clear_type', size=(11, 1), background_color='#7799fd', text_color='#000000'),
            sg.Text('NEW', visible=False, key='result_clear_type_new', background_color='#7799fd', text_color='#000000')
        ],
        [
            sg.Text('DJレベル', size=(22, 1)),
            sg.Text(key='result_dj_level', size=(11, 1), background_color='#7799fd', text_color='#000000'),
            sg.Text('NEW', visible=False, key='result_dj_level_new', background_color='#7799fd', text_color='#000000')
        ],
        [
            sg.Text('スコア', size=(22, 1)),
            sg.Text(key='result_score', size=(11, 1), background_color='#7799fd', text_color='#000000'),
            sg.Text('NEW', visible=False, key='result_score_new', background_color='#7799fd', text_color='#000000')
        ],
        [
            sg.Text('ミスカウント', size=(22, 1)),
            sg.Text(key='result_miss_count', size=(11, 1), background_color='#7799fd', text_color='#000000'),
            sg.Text('NEW', visible=False, key='result_miss_count_new', background_color='#7799fd', text_color='#000000')
        ]
    ]

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
        [
            sg.Button('トリム', key='button_trim'),
            sg.Button('更新', key='button_define_overwrite', tooltip='トリム範囲を定義保存')
        ],
        [sg.Image(key='trim')],
        [sg.Button('検索イメージ保存', key='button_find_save', visible=False)],
    ]

    manage_label_define = [
        [sg.Text('起動', size=(15, 1)), sg.Combo(selectable_value_list['startings'], key='starting', readonly=True)],
        [sg.Text('リザルト判定', size=(15, 1)), sg.Checkbox('認識可能', key='trigger', default=True)],
        [
            sg.Text('カットイン', size=(15, 1)),
            sg.Checkbox('ミッション', key='cutin_mission'),
            sg.Checkbox('ビット獲得', key='cutin_bit')
        ],
        [sg.Text('ライバル挑戦状', size=(15, 1)), sg.Checkbox('表示中', key='rival', default=False)],
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
            sg.Text('プレイサイド', size=(15, 1)),
            sg.Radio('なし', key='play_side_none', group_id='play_side', default=True),
            sg.Radio('1P', key='play_side_1p', group_id='play_side'),
            sg.Radio('2P', key='play_side_2p', group_id='play_side')
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
                    sg.Text('/', background_color='#7799fd'),
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
            ], background_color='#7799fd', pad=0)
        ],
        [
            sg.Text('特殊オプション', size=(15, 1)),
            sg.Check('BATTLE', key='option_battle'),
            sg.Check('H-RANDOM', key='option_h-random')
        ],
        [
            sg.Text('クリアタイプ', size=(15, 1)),
            sg.Combo(selectable_value_list['clear_types'], key='clear_type', size=(11, 1), readonly=True),
            sg.Checkbox('NEW', key='clear_type_new')
        ],
        [
            sg.Text('DJレベル', size=(15, 1)),
            sg.Combo(selectable_value_list['dj_levels'], key='dj_level', size=(11, 1), readonly=True),
            sg.Checkbox('NEW', key='dj_level_new')
        ],
        [
            sg.Text('スコア', size=(15, 1)),
            sg.Input(key='score', size=(12, 1)),
            sg.Checkbox('NEW', key='score_new')
        ],
        [
            sg.Text('ミスカウント', size=(15, 1)),
            sg.Input(key='miss_count', size=(12, 1)),
            sg.Checkbox('NEW', key='miss_count_new')
        ],
        [
            sg.Button('アノテーション保存', key='button_label_overwrite'),
            sg.Button('認識結果から引用', key='button_recog')
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
                    sg.Column(area_define, size=(300, 410), background_color='#7799fd'),
                    sg.Column(manage_result, size=(310, 410), background_color='#7799fd'),
                    sg.Column(result, size=(380, 410), background_color='#7799fd')
                ],
            ],pad=0),
            sg.Column([
                [sg.Column(manage_label_define, size=(450, 815), background_color='#7799fd')],
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

def set_result(result):
    window['starting'].update('')
    window['trigger'].update(True)
    window['cutin_mission'].update(False)
    window['cutin_bit'].update(False)
    window['rival'].update(result.rival)
    window['play_mode'].update(result.informations['play_mode'])
    window['difficulty'].update(result.informations['difficulty'])
    window['level'].update(result.informations['level'])
    window['music'].update(result.informations['music'])
    if result.play_side == '1P':
        window['play_side_1p'].update(True)
    if result.play_side == '2P':
        window['play_side_2p'].update(True)

    if result.details['option_arrange'] is not None:
        if result.details['option_arrange'] in value_list['options_arrange']:
            window['option_arrange'].update(result.details['option_arrange'])
        if '/' in result.details['option_arrange']:
            left, right = result.details['option_arrange'].split('/')
            window['option_arrange_1p'].update(left)
            window['option_arrange_2p'].update(right)
        if result.details['option_arrange'] in value_list['options_arrange_sync']:
            window['option_arrange_sync'].update(result.details['option_arrange'])

    window['option_flip'].update(result.details['option_flip'])
    window['option_assist'].update(result.details['option_assist'])
    window['option_battle'].update(result.details['option_battle'])
    window['option_h-random'].update(result.details['option_h-random'])
    window['clear_type'].update(result.details['clear_type'])
    window['clear_type_new'].update(result.details['clear_type_new'])
    window['dj_level'].update(result.details['dj_level'])
    window['dj_level_new'].update(result.details['dj_level_new'])
    window['score'].update(result.details['score'])
    window['score_new'].update(result.details['score_new'])
    window['miss_count'].update(result.details['miss_count'])
    window['miss_count_new'].update(result.details['miss_count_new'])

def set_labels(label):
    window['starting'].update('')
    window['trigger'].update(True)
    window['cutin_mission'].update(False)
    window['cutin_bit'].update(False)
    window['rival'].update(False)
    window['play_mode'].update('')
    window['difficulty'].update('')
    window['level'].update('')
    window['play_side_none'].update(True)
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
        if 'play_mode' in label.keys():
            window['play_mode'].update(label['play_mode'])
        if 'difficulty' in label.keys():
            window['difficulty'].update(label['difficulty'])
        if 'level' in label.keys():
            window['level'].update(label['level'])
        if 'music' in label.keys():
            window['music'].update(label['music'])
        if 'play_side' in label.keys():
            if label['play_side'] == '1P':
                window['play_side_1p'].update(True)
            if label['play_side'] == '2P':
                window['play_side_2p'].update(True)
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

def set_recognition(screen):
    window['recog_starting'].update(recog.get_starting(screen.image))
    window['recog_trigger'].update(visible=recog.search_trigger(screen.image))
    window['recog_cutin_mission'].update(visible=recog.search_cutin_mission(screen.image))
    window['recog_cutin_bit'].update(visible=recog.search_cutin_bit(screen.image))

    if not recog.is_result(screen.image):
        window['result_play_mode'].update('')
        window['result_difficulty'].update('')
        window['result_level'].update('')
        window['result_music'].update('')
        window['result_rival'].update(visible=False)
        window['result_play_side'].update('')
        window['result_use_option'].update(visible=False)
        window['result_option_arrange'].update('')
        window['result_option_assist'].update('')
        window['result_option_flip'].update('')
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
        return

    result = recog.get_result(screen)

    window['result_play_mode'].update(result.informations['play_mode'])
    window['result_difficulty'].update(result.informations['difficulty'])
    window['result_level'].update(result.informations['level'])
    window['result_music'].update(result.informations['music'])

    window['result_rival'].update(visible=result.rival)
    window['result_play_side'].update(result.play_side)
    
    window['result_use_option'].update(visible=result.details['use_option'] is not None)
    if result.details['use_option'] is not None:
        window['result_option_arrange'].update(result.details['option_arrange'])
        window['result_option_flip'].update(result.details['option_flip'])
        window['result_option_assist'].update(result.details['option_assist'])
        window['result_option_battle'].update(visible=result.details['option_battle'])
        window['result_option_h-random'].update(visible=result.details['option_h-random'])
    else:
        window['result_option_arrange'].update('')
        window['result_option_flip'].update('')
        window['result_option_assist'].update('')
        window['result_option_battle'].update(visible=False)
        window['result_option_h-random'].update(visible=False)

    window['result_clear_type'].update(result.details['clear_type'])
    window['result_dj_level'].update(result.details['dj_level'])
    window['result_score'].update(result.details['score'])
    window['result_miss_count'].update(result.details['miss_count'])
    window['result_clear_type_new'].update(visible=result.details['clear_type_new'])
    window['result_dj_level_new'].update(visible=result.details['dj_level_new'])
    window['result_score_new'].update(visible=result.details['score_new'])
    window['result_miss_count_new'].update(visible=result.details['miss_count_new'])
