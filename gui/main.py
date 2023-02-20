import PySimpleGUI as sg
import io
from PIL import Image

from define import define
from .static import title,icon_path,background_color,background_color_label
from record import get_recode_musics

scales = ['1/1', '1/2', '1/4']

icon_image = Image.open(icon_path)
resized_icon = icon_image.resize((32, 32))
icon_bytes = io.BytesIO()
resized_icon.save(icon_bytes, format='PNG')

def layout_main(setting):
    column_headers = ['日時', '曲名', 'M', 'CT', 'DL', 'SC', 'MC']
    column_widths = [13, 13, 4, 3, 3, 3, 3]

    if setting.display_music:
        column_visibles = [False, True, True, True, True, True, True]
    else:
        column_visibles = [True, False, True, True, True, True, True]

    tabs_main = [[
        sg.Tab('今日のリザルト', [
            [sg.Table(
                [],
                key='table_results',
                headings=column_headers,
                auto_size_columns=False,
                vertical_scroll_only=True,
                col_widths=column_widths,
                visible_column_map=column_visibles,
                num_rows=17,
                justification='center',
                enable_events=True,
                background_color=background_color
            )]
        ], pad=0, background_color=background_color),
        sg.Tab('曲検索', [
            [
                sg.Text('プレイモード', size=(12, 1), background_color=background_color_label),
                sg.Radio('SP', group_id='play_mode', key='play_mode_sp', enable_events=True, background_color=background_color),
                sg.Radio('DP', group_id='play_mode', key='play_mode_dp', enable_events=True, background_color=background_color)
            ],
            [
                sg.Text('譜面難易度', size=(12, 1), background_color=background_color_label),
                sg.Combo(define.value_list['difficulties'], key='difficulty', readonly=True, enable_events=True, size=(14, 1))
            ],
            [
                sg.Text('曲名', size=(12, 1), background_color=background_color),
                sg.Input(key='search_music', size=(20,1), enable_events=True)
            ],
            [
                sg.Column([
                    [
                        sg.Listbox([], key='music_candidates', size=(18,13), right_click_menu=['menu', ['選択した曲の記録を削除する']], enable_events=True),
                        sg.Listbox([], key='history', size=(15,13), right_click_menu=['menu', ['選択したリザルトの記録を削除する']], horizontal_scroll=True, enable_events=True)
                    ]
                ], pad=0, background_color=background_color)
            ]
        ], pad=0, background_color=background_color)
    ]]

    tabs_sub = [[
        sg.Tab('ベスト', [
            [
                sg.Text('クリアタイプ', size=(11, 1), background_color=background_color_label, font=('Arial', 9)),
                sg.Text(key='clear_type', size=(10, 1), background_color=background_color),
                sg.Text(key='clear_type_timestamp', size=(13, 1), background_color=background_color, text_color='#dddddd')
            ],
            [
                sg.Text('DJレベル', size=(11, 1), background_color=background_color_label, font=('Arial', 9)),
                sg.Text(key='dj_level', size=(10, 1), background_color=background_color),
                sg.Text(key='dj_level_timestamp', size=(13, 1), background_color=background_color, text_color='#dddddd')
            ],
            [
                sg.Text('スコア', size=(11, 1), background_color=background_color_label, font=('Arial', 9)),
                sg.Text(key='score', size=(10, 1), background_color=background_color),
                sg.Text(key='score_timestamp', size=(13, 1), background_color=background_color, text_color='#dddddd')
            ],
            [
                sg.Text('ミスカウント', size=(11, 1), background_color=background_color_label, font=('Arial', 9)),
                sg.Text(key='miss_count', size=(10, 1), background_color=background_color),
                sg.Text(key='miss_count_timestamp', size=(13, 1), background_color=background_color, text_color='#dddddd')
            ]
        ], pad=0, background_color=background_color),
        sg.Tab('履歴', [
            [
                sg.Text('日時', size=(11, 1), background_color=background_color_label, font=('Arial', 9)),
                sg.Text(key='history_timestamp', size=(13, 1), background_color=background_color)
            ],
            [
                sg.Text('クリアタイプ', size=(11, 1), background_color=background_color_label, font=('Arial', 9)),
                sg.Text(key='history_clear_type', size=(10, 1), background_color=background_color)
            ],
            [
                sg.Text('DJレベル', size=(11, 1), background_color=background_color_label, font=('Arial', 9)),
                sg.Text(key='history_dj_level', size=(10, 1), background_color=background_color)
            ],
            [
                sg.Text('スコア', size=(11, 1), background_color=background_color_label, font=('Arial', 9)),
                sg.Text(key='history_score', size=(10, 1), background_color=background_color)
            ],
            [
                sg.Text('ミスカウント', size=(11, 1), background_color=background_color_label, font=('Arial', 9)),
                sg.Text(key='history_miss_count', size=(10, 1), background_color=background_color)
            ],
            [
                sg.Text('オプション', size=(11, 1), background_color=background_color_label, font=('Arial', 9)),
                sg.Text(key='history_options', size=(25, 1), background_color=background_color)
            ]
        ], pad=0, background_color=background_color)
    ]]

    pane_left = [
        [
            sg.Text('画像表示スケール', background_color=background_color),
            sg.Combo(scales, key='scale', default_value='1/2', readonly=True),
            sg.Text('INFINITASを見つけました', key='positioned', background_color=background_color, font=('Arial', 10, 'bold'), text_color='#f0fc80', visible=False)
        ],
        [
            sg.Column([
                [sg.Checkbox('更新があるときのみリザルトを記録する', key='check_newrecord_only', default=setting.newrecord_only, enable_events=True, background_color=background_color)],
                [sg.Checkbox('自動で画像をファイルに保存する', key='check_autosave', default=setting.autosave, enable_events=True, background_color=background_color)],
                [sg.Checkbox('自動でライバルを隠した画像をファイルに保存する', key='check_autosave_filtered', default=setting.autosave_filtered, enable_events=True, background_color=background_color)],
                [sg.Checkbox('INFINITASを見つけたときと記録したときに音を出す', key='check_play_sound', default=setting.play_sound, enable_events=True, background_color=background_color)]
            ], pad=0, background_color=background_color, vertical_alignment='top'),
            sg.Column([
                [sg.Checkbox('リザルトを都度表示する', key='check_display_result', default=setting.display_result, enable_events=True, background_color=background_color)],
                [sg.Checkbox('曲名を表示する', key='check_display_music', default=setting.display_music, enable_events=True, background_color=background_color)]
            ], pad=0, background_color=background_color, vertical_alignment='top')
        ],
        [sg.Image(key='screenshot', size=(640, 360), background_color=background_color)],
        [
            sg.Button('ファイルに保存する', key='button_save', disabled=True),
            sg.Button('ライバルを隠して保存する', key='button_save_filtered', disabled=True),
            sg.Checkbox('収集データを必ずアップロードする', key='force_upload', visible=setting.manage, background_color=background_color)
        ]
    ]

    pane_right = [
        [
            sg.TabGroup(
                tabs_main,
                pad=0,
                background_color=background_color,
                tab_background_color=background_color,
                selected_background_color='#245d18'
            )
        ],
        [
            sg.Text('最終プレイ', size=(11, 1), background_color=background_color_label),
            sg.Text(key='latest', size=(13, 1), background_color=background_color),
            sg.Button('グラフ', key='button_graph')
        ],
        [
            sg.TabGroup(
                tabs_sub,
                pad=0,
                background_color=background_color,
                tab_background_color=background_color,
                selected_background_color='#245d18'
            )
        ]
    ]

    return [
        [
            sg.Column([
                [
                    sg.Text('Ctrl+F10でスクリーンショットを保存', visible=setting.manage, background_color=background_color),
                    sg.Checkbox('スクリーンショットを常時表示する', key='check_display_screenshot', visible=setting.manage, enable_events=True, background_color=background_color)
                ],
                [
                    sg.Column(pane_left, pad=0, background_color=background_color),
                    sg.Column(pane_right, pad=0, background_color=background_color)
                ]
            ], pad=0, background_color=background_color),
            sg.Output(key='output', size=(30, 34), visible=setting.manage)
        ]
    ]

def generate_window(setting, version):
    global window

    window = sg.Window(
        f'{title} ({version})',
        layout_main(setting),
        icon=icon_path,
        grab_anywhere=True,
        return_keyboard_events=True,
        resizable=False,
        finalize=True,
        enable_close_attempted_event=True,
        background_color=background_color
    )

    return window

def collection_request(image):
    ret = sg.popup_yes_no(
        '\n'.join([
            u'曲名の画像認識の精度向上のためにリザルト画像を欲しています。',
            u'リザルト画像を上画像のように切り取ってクラウドにアップロードします。',
            u'',
            u'もちろん、他の目的に使用することはしません。',
            u'',
            u'曲名の認識精度が上がるほど、曲名表示が?????になることは減っていきます。',
            u'',
            u'画像のアップロードを許可しますか？'
        ]),
        title=u'おねがい',
        image=image,
        icon=icon_path,
        background_color=background_color
    )

    return True if ret == 'Yes' else False

def find_latest_version(latest_url):
    sg.popup_scrolled(
        '\n'.join([
            u'最新バージョンが見つかりました。',
            u'以下URLから最新バージョンをダウンロードしてください。',
            u'\n',
            latest_url
        ]),
        title=u'最新バージョンのお知らせ',
        icon=icon_path,
        size=(60, 6),
        background_color=background_color
    )

def error_message(title, message, exception):
    sg.popup(
        '\n'.join([
            message,
            '\n',
            str(exception)
        ]),
        title=title,
        icon=icon_path
    )

def display_image(image, savable=False, filterable=False):
    subsample = int(window['scale'].get().split('/')[1])
    
    if image is not None:
        bytes = io.BytesIO()
        image.save(bytes, format='PNG')
        window['screenshot'].update(data=bytes.getvalue(), subsample=subsample, visible=True)
    else:
        savable = False
        filterable = False
        window['screenshot'].update(visible=False)

    window['button_save'].update(disabled=image is None or not savable)
    window['button_save_filtered'].update(disabled=not filterable)

def switch_table(display_music):
    if not display_music:
        displaycolumns = ['日時', 'M', 'CT', 'DL', 'SC', 'MC']
    else:
        displaycolumns = ['曲名', 'M', 'CT', 'DL', 'SC', 'MC']

    window['table_results'].Widget.configure(displaycolumns=displaycolumns)

def search_music_candidates():
    search_music = window['search_music'].get()
    if len(search_music) != 0:
        musics = get_recode_musics()
        candidates = [music for music in musics if search_music in music]
        window['music_candidates'].update(values=candidates)
    else:
        window['music_candidates'].update(values=[])

def display_record(record):
    if record is None:
        window['history'].update([])
        window['latest'].update('')
        window['history_timestamp'].update('')
        window['history_options'].update('')
        for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
            window[key].update('')
            window[f'{key}_timestamp'].update('')
            window[f'history_{key}'].update('')
        return
    
    latest_timestamp = record['latest']['timestamp']
    formatted_timestamp = f'{int(latest_timestamp[0:4])}年{int(latest_timestamp[4:6])}月{int(latest_timestamp[6:8])}日'
    window['latest'].update(formatted_timestamp)

    window['history'].update([*reversed(record['timestamps'])])

    if 'best' in record.keys():
        for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
            if key in record['best']:
                value = record['best'][key]['value']
                timestamp = record['best'][key]['timestamp']
                timestamp = f'{int(timestamp[0:4])}年{int(timestamp[4:6])}月{int(timestamp[6:8])}日'
                window[key].update(value if value is not None else '')
                window[f'{key}_timestamp'].update(timestamp)
            else:
                window[key].update('')
                window[f'{key}_timestamp'].update('')
    else:
        for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
            window[key].update('')
            window[f'{key}_timestamp'].update('')
    
    window['history_timestamp'].update('')
    for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
        window[f'history_{key}'].update('')
    window['history_options'].update('')

def display_historyresult(record, timestamp):
    formatted_timestamp = f'{int(timestamp[0:4])}年{int(timestamp[4:6])}月{int(timestamp[6:8])}日'
    window['history_timestamp'].update(formatted_timestamp)

    target = record['history'][timestamp]
    for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
        window[f'history_{key}'].update(target[key]['value'] if target[key]['value'] is not None else '')
    if not 'options' in target.keys() or target['options'] is None:
        window['history_options'].update('不明')
    else:
        window['history_options'].update(' '.join([
            target['options']['arrange'] if target['options']['arrange'] is not None else '',
            target['options']['flip'] if target['options']['flip'] is not None else '',
            target['options']['assist'] if target['options']['assist'] is not None else '',
            'BATTLE' if target['options']['battle'] else ''
        ]))
    
