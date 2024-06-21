import PySimpleGUI as sg

from define import define
from resources import resource
from .static import (
    title,
    icon_path,
    background_color,
    background_color_label,
    background_color2_label,
    selected_background_color,
    textcolor_shadow,
    textcolor_highlight,
)
from .menubar import MenuBar
from setting import Setting

font_smallbutton = ('Arial', 9)

best_display_modes = ('option', 'timestamp', )

best_display_mode = best_display_modes[0]

discod_webhook_displayvalues_mode = {
    'battle': 'B',
    'score': 'SC',
    'misscount': 'MC'
}

discod_webhook_displayvalues_state = {
    'active': '*',
    'nonactive': '',
    'error': '--'
}

menubar: list = [
    [MenuBar.Text('ファイル', key='F'), [
        MenuBar.Text('リザルト画像フォルダを開く', key='R'),
        MenuBar.Text('ライバル隠し画像フォルダを開く', key='F'),
        MenuBar.Text('譜面記録画像フォルダを開く', key='I'),
        MenuBar.Text('グラフ画像フォルダを開く', key='G'),
        MenuBar.Line(),
        MenuBar.Text('エクスポートフォルダを開く', key='E'),
        MenuBar.Line(),
        MenuBar.Text('終了', key='X'),
    ]],
    [MenuBar.Text('譜面', key='S'), [
        MenuBar.Text('グラフ画像の作成', key='C'),
        MenuBar.Line(),
        MenuBar.Text('譜面記録画像の保存', key='I'),
        MenuBar.Text('グラフ画像の保存', key='G'),
        MenuBar.Line(),
        MenuBar.Text('譜面記録のポスト', key='P'),
    ]],
    [MenuBar.Text('リザルト', key='R'), [
        MenuBar.Text('画像保存', key='S'),
        MenuBar.Text('ライバルを隠す', key='F'),
        MenuBar.Text('Xにポスト', key='P'),
    ]],
    [MenuBar.Text('設定', key='S'), [
        MenuBar.Text('設定を開く', key='S'),
        MenuBar.Text('エクスポートを開く', key='E'),
        MenuBar.Line(),
        MenuBar.Text('CSV出力', key='P'),
        MenuBar.Line(),
        MenuBar.Text('最近のデータのリセット', key='R'),
    ]],
]

def layout_main(setting: Setting):
    column_headers = ['S', 'F', '日時', '曲名', 'MODE', 'CT', 'DL', 'SC', 'MC']
    column_widths = [3, 3, 16, 16, 5, 3, 3, 3, 3]

    if setting.display_music:
        column_visibles = [True, True, False, True, True, True, True, True, True]
    else:
        column_visibles = [True, True, True, False, True, True, True, True, True]

    if not resource.musictable is None:
        versions = ['ALL', *resource.musictable['versions']]
    else:
        versions = ['ALL']

    djname = setting.discord_webhook['djname'] if 'djname' in setting.discord_webhook.keys() else ''
    tabs_main = [[
        sg.Tab('最近のリザルト', [
            [sg.Table(
                [],
                header_font=('Arial', 8),
                font=('Arial', 9),
                key='table_results',
                headings=column_headers,
                auto_size_columns=False,
                vertical_scroll_only=True,
                col_widths=column_widths,
                visible_column_map=column_visibles,
                num_rows=16,
                justification='center',
                enable_events=True,
                background_color=background_color
            )],
            [
                sg.Button('画像保存', key='button_save_results', disabled=True, font=font_smallbutton, pad=1),
                sg.Button('ライバル隠して保存', key='button_filter_results', disabled=True, font=font_smallbutton, pad=1),
                sg.Button('ポスト', key='button_post_results', disabled=True, font=font_smallbutton, pad=1),
                sg.Button('誤認識の通報', key='button_upload_results', disabled=True, font=font_smallbutton, pad=1, visible=setting.data_collection),
            ],
        ], pad=0, background_color=background_color),
        sg.Tab('曲検索', [
            [
                sg.Text('バージョン', size=(12, 1), background_color=background_color_label),
                sg.Combo(versions, default_value='ALL', key='category_versions', readonly=True, enable_events=True, size=(20, 1))
            ],
            [
                sg.Text('曲名絞り込み', size=(12, 1), background_color=background_color_label),
                sg.Input(key='search_music', size=(20,1), enable_events=True)
            ],
            [
                sg.Text('プレイモード', size=(12, 1), background_color=background_color2_label),
                sg.Radio('SP', group_id='play_mode', key='play_mode_sp', enable_events=True, background_color=background_color),
                sg.Radio('DP', group_id='play_mode', key='play_mode_dp', enable_events=True, background_color=background_color)
            ],
            [
                sg.Text('譜面難易度', size=(12, 1), background_color=background_color2_label),
                sg.Combo(define.value_list['difficulties'], key='difficulty', readonly=True, enable_events=True, size=(14, 1))
            ],
            [
                sg.Column([
                    [
                        sg.Listbox(
                            [*resource.musictable['musics'].keys()] if not resource.musictable is None else [],
                            key='music_candidates',
                            font=('Arial', 9),
                            size=(20,8),
                            horizontal_scroll=True,
                            enable_events=True
                        ),
                        sg.Listbox(
                            [],
                            key='history',
                            font=('Arial', 9),
                            size=(15,9),
                            enable_events=True
                        )
                    ]
                ], pad=0, background_color=background_color),
            ],
            [
                sg.Button('選択曲の記録全削除', key='delete_selectmusic', font=font_smallbutton, disabled=True),
                sg.Button('選択記録の削除', key='delete_selectresult', font=font_smallbutton, disabled=True),
            ]
        ], pad=0, background_color=background_color),
        sg.Tab('連携投稿', [
            [
                sg.Text('名前', size=(12, 1), background_color=background_color_label),
                sg.Input(djname, key='discord_webhook_djname', size=(10,1)),
                sg.Button('保存', key='discord_webhook_savedjname')
            ],
            [
                sg.Table(
                    [],
                    header_font=('Arial', 8),
                    font=('Arial', 9),
                    key='discord_webhooks_list',
                    headings=['Name', 'M', 'State', 'Best'],
                    auto_size_columns=False,
                    vertical_scroll_only=True,
                    col_widths=[24, 4, 5, 5],
                    num_rows=4,
                    justification='center',
                    enable_events=True,
                    background_color=background_color
                )
            ],
            [
                sg.Button('追加', key='discord_webhook_add'),
                sg.Button('更新', key='discord_webhook_update'),
                sg.Button('有効化', key='discord_webhook_activate'),
                sg.Button('無効化', key='discord_webhook_deactivate'),
                sg.Button('削除', key='discord_webhook_delete')
            ],
            [
                sg.Listbox(
                    [],
                    key='discord_webhooks_log',
                    size=(38, 6),
                    horizontal_scroll=True
                )
            ]
        ], pad=0, background_color=background_color),
        sg.Tab('レーダー', [
            [
                sg.Text('プレイモード', size=(12, 1), background_color=background_color2_label),
                sg.Radio('SP', group_id='notesradar_playmode', key='notesradar_playmode_sp', enable_events=True, background_color=background_color),
                sg.Radio('DP', group_id='notesradar_playmode', key='notesradar_playmode_dp', enable_events=True, background_color=background_color)
            ],
            [
                sg.Text('TOTAL', size=(12, 1), background_color=background_color2_label),
                sg.Text('', key='notesradar_total', background_color=background_color)
            ],
            [
                sg.Combo(['', *define.value_list['notesradar_attributes']], size=(12, 1), key='notesradar_attribute', readonly=True, enable_events=True),
                sg.Text('', key='notesradar_value', background_color=background_color)
            ],
            [
                sg.Radio('対象10位', group_id='notesradar_tablemode', key='notesradar_tablemode_averagetarget', enable_events=True, background_color=background_color, default=True),
                sg.Radio('上位50曲', group_id='notesradar_tablemode', key='notesradar_tablemode_top30', enable_events=True, background_color=background_color)
            ],
            [
                sg.Table(
                    [],
                    header_font=('Arial', 8),
                    font=('Arial', 9),
                    key='notesradar_ranking',
                    headings=['No.', 'Music', 'D', 'Point'],
                    auto_size_columns=False,
                    vertical_scroll_only=True,
                    col_widths=[3, 25, 3, 7],
                    num_rows=10,
                    justification='center',
                    enable_events=True,
                    background_color=background_color
                )
            ]
        ], pad=0, background_color=background_color)
    ]]

    tabs_sub = [[
        sg.Tab('ベスト', [
            [
                sg.Text('クリアタイプ', size=(11, 1), background_color=background_color_label, font=('Arial', 9)),
                sg.Text(key='best_clear_type', size=(10, 1), background_color=background_color),
                sg.Text(key='best_clear_type_option', size=(13, 1), background_color=background_color, text_color='#eeeeee'),
                sg.Text(key='best_clear_type_timestamp', size=(13, 1), visible=False, background_color=background_color, text_color='#eeeeee'),
            ],
            [
                sg.Text('DJレベル', size=(11, 1), background_color=background_color_label, font=('Arial', 9)),
                sg.Text(key='best_dj_level', size=(10, 1), background_color=background_color),
                sg.Text(key='best_dj_level_option', size=(13, 1), background_color=background_color, text_color='#eeeeee'),
                sg.Text(key='best_dj_level_timestamp', size=(13, 1), visible=False, background_color=background_color, text_color='#eeeeee'),
            ],
            [
                sg.Text('スコア', size=(11, 1), background_color=background_color_label, font=('Arial', 9)),
                sg.Text(key='best_score', size=(10, 1), background_color=background_color),
                sg.Text(key='best_score_option', size=(13, 1), background_color=background_color, text_color='#eeeeee'),
                sg.Text(key='best_score_timestamp', size=(13, 1), visible=False, background_color=background_color, text_color='#eeeeee'),
            ],
            [
                sg.Text('ミスカウント', size=(11, 1), background_color=background_color_label, font=('Arial', 9)),
                sg.Text(key='best_miss_count', size=(10, 1), background_color=background_color),
                sg.Text(key='best_miss_count_option', size=(13, 1), background_color=background_color, text_color='#eeeeee'),
                sg.Text(key='best_miss_count_timestamp', size=(13, 1), visible=False, background_color=background_color, text_color='#eeeeee'),
            ],
            [
                sg.Button('使用オプション >> 更新日', size=(26, 1), key='button_best_switch')
            ]
        ], pad=0, background_color=background_color),
        sg.Tab('履歴', [
            [
                sg.Text('日時', size=(11, 1), background_color=background_color_label, font=('Arial', 9)),
                sg.Text(key='history_timestamp', size=(25, 1), background_color=background_color)
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
            sg.Text('INFINITASを見つけました', key='detect_infinitas', background_color=background_color, font=('Arial', 10, 'bold'), text_color=textcolor_shadow),
            sg.Text('スクショ可能', key='capture_enable', background_color=background_color, font=('Arial', 10, 'bold'), text_color=textcolor_shadow)
        ],
        [
            sg.TabGroup([[
                    sg.Tab('インフォメーション', [
                        [sg.Image(key='image_information', size=(640, 360), background_color=background_color)],
                    ], key='tab_main_information', pad=0, background_color=background_color),
                    sg.Tab('統計', [
                        [sg.Image(key='image_summary', size=(640, 360), background_color=background_color)],
                        [
                            sg.Button('カウント方式 切替', key='button_summary_switch'),
                            sg.Button('表示内容 設定', key='button_summary_setting'),
                            sg.Button('統計のポスト', key='button_post_summary', disabled=True),
                            sg.Button('エクスポートフォルダを開く', key='button_openfolder_export_summary'),
                        ],
                    ], key='tab_main_summary', pad=0, background_color=background_color),
                    sg.Tab('ノーツレーダー', [
                        [sg.Image(key='image_notesradar', size=(640, 360), background_color=background_color)],
                        [
                            sg.Button('ノーツレーダーのポスト', key='button_post_notesradar', disabled=True),
                            sg.Button('エクスポートフォルダを開く', key='button_openfolder_export_notesradar'),
                        ],
                    ], key='tab_main_notesradar', pad=0, background_color=background_color),
                    sg.Tab('スクリーンショット', [
                        [sg.Image(key='image_screenshot', size=(640, 360), background_color=background_color)],
                        [
                            sg.Button('リザルトフォルダを開く', key='button_openfolder_results'),
                            sg.Button('ライバル隠しフォルダを開く', key='button_openfolder_filtereds'),
                            sg.Text('', key='screenshot_filepath', font=('Arial', 9, 'bold'), text_color=textcolor_highlight, background_color=background_color)
                        ],
                    ], key='tab_main_screenshot', pad=0, background_color=background_color),
                    sg.Tab('譜面記録', [
                        [sg.Image(key='image_scoreinformation', size=(640, 360), background_color=background_color)],
                        [
                            sg.Button('画像保存', key='button_save_scoreinformation', disabled=True),
                            sg.Button('譜面記録のポスト', key='button_post_scoreinformation', disabled=True),
                            sg.Button('フォルダを開く', key='button_openfolder_scoreinformations'),
                        ],
                    ], key='tab_main_scoreinformation', pad=0, background_color=background_color),
                    sg.Tab('グラフ', [
                        [sg.Image(key='image_graph', size=(640, 360), background_color=background_color, enable_events=True)],
                        [
                            sg.Button('画像保存', key='button_save_graph', disabled=True),
                            sg.Button('譜面記録のポスト', key='button_post_graph', disabled=True),
                            sg.Button('フォルダを開く', key='button_openfolder_graphs'),
                        ],
                    ], key='tab_main_graph', pad=0, background_color=background_color),
                ]],
                background_color=background_color,
                tab_background_color=background_color,
                selected_background_color='#245d18'
            )
        ],
        [
            sg.Button('設定', key='button_setting', size=(14, 1)),
            sg.Button('エクスポート', key='button_export', size=(14, 1)),
        ],
    ]

    pane_right = [
        [
            sg.TabGroup(
                tabs_main,
                pad=0,
                background_color=background_color,
                tab_background_color=background_color,
                selected_background_color=selected_background_color
            )
        ],
        [
            sg.Text('プレイ回数', size=(11, 1), background_color=background_color_label),
            sg.Text(key='played_count', size=(5, 1), background_color=background_color),
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
            sg.Menu(MenuBar.Compile(menubar), key='menu'),
            sg.Column([
                [
                    sg.Column(
                        pane_left,
                        pad=0,
                        background_color=background_color,
                        vertical_alignment="top"
                    ),
                    sg.Column(
                        pane_right,
                        pad=0,
                        background_color=background_color,
                        vertical_alignment="top"
                    )
                ]
            ], pad=0, background_color=background_color),
        ]
    ]

def set_discord_servers(servers):
    """設定をテーブルにセットする
    """
    values = []
    names = []
    for name, value in servers.items():
        if value['mode'] == 'battle':
            mybest = '---'
        else:
            mybest = value['mybest'] if value['mybest'] is not None else ''
        values.append([
            name,
            discod_webhook_displayvalues_mode[value['mode']],
            discod_webhook_displayvalues_state[value['state']],
            mybest
        ])
        names.append(name)

    window['discord_webhooks_list'].update(values)

    return names

def generate_window(setting, version):
    global window

    window = sg.Window(
        f'{title} ({version})',
        layout_main(setting),
        icon=icon_path,
        return_keyboard_events=True,
        resizable=False,
        finalize=True,
        enable_close_attempted_event=True,
        background_color=background_color
    )

    return window

def generate_window_debug():
    return sg.Window(
        'デバッグコンソール', 
        [
            [sg.Output(key='output', size=(90, 30))],
            [
                sg.InputText(key='text_file_path', size=(70, 1), enable_events=True),
                sg.FileBrowse("ファイルを開く", target="text_file_path")
            ],
            [sg.Checkbox('常時キャプチャー表示', key='check_display_screenshot', enable_events=True)],
            [sg.Checkbox('収集データを必ずアップロードする', key='force_upload', enable_events=True)],
        ],
        finalize=True,
        enable_close_attempted_event=True,
    )

def update_musictable():
    window['category_versions'].update(
        'ALL',
        values=['ALL', *resource.musictable['versions'].keys()]
    )
    search_music_candidates()

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

def error_message(title, message, exception):
    sg.popup(
        '\n'.join([message, '\n', str(exception)]),
        title=title,
        icon=icon_path,
        background_color=background_color
    )

def displayimage(target: sg.Image, value: bytes):
    if value is not None:
        target.update(data=value, subsample=2)
    else:
        target.update(data=resource.imagevalue_imagenothing, subsample=2)

def switch_table(display_music):
    if not display_music:
        displaycolumns = ['S', 'F', '日時', 'MODE', 'CT', 'DL', 'SC', 'MC']
    else:
        displaycolumns = ['S', 'F', '曲名', 'MODE', 'CT', 'DL', 'SC', 'MC']

    window['table_results'].Widget.configure(displaycolumns=displaycolumns)

def search_music_candidates():
    version = window['category_versions'].get()
    music_piece = window['search_music'].get()

    musics = resource.musictable['musics']

    candidates = [music for music in musics if (version == 'ALL' or music in resource.musictable['versions'][version]) and music_piece in music]

    window['music_candidates'].update(values=candidates)

def display_record(record: dict, timestamp: str=None):
    if record is None:
        window['history'].update([])
        window['played_count'].update('')
        window['history_timestamp'].update('')
        window['history_options'].update('')
        for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
            window[f'best_{key}'].update('')
            window[f'best_{key}_option'].update('')
            window[f'best_{key}_timestamp'].update('')
            window[f'history_{key}'].update('')

        window['delete_selectmusic'].update(disabled=True)
        window['delete_selectresult'].update(disabled=True)

        return

    if 'timestamps' in record.keys():
        reversedlist = [*reversed(record['timestamps'])]
        if timestamp is not None and timestamp in reversedlist:
            window['history'].update(reversedlist, set_to_index=[reversedlist.index(timestamp)])
        else:
            window['history'].update(reversedlist)
        window['played_count'].update(len(record['timestamps']))
    else:
        window['history'].update([])
        window['played_count'].update(0)

    if 'best' in record.keys():
        for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
            if key in record['best'] and record['best'][key] is not None:
                value = record['best'][key]['value']
                if 'options' in record['best'][key].keys() and record['best'][key]['options'] is not None:
                    if record['best'][key]['options']['arrange'] is not None:
                        option = record['best'][key]['options']['arrange']
                    else:
                        option = '---------'
                else:
                    option = '?????'
                if record['best'][key]['timestamp'] is not None:
                    timestamp = record['best'][key]['timestamp']
                    formatted_timestamp = f'{int(timestamp[0:4])}年{int(timestamp[4:6])}月{int(timestamp[6:8])}日'
                else:
                    formatted_timestamp = '?????'
                window[f'best_{key}'].update(value if value is not None else '')
                window[f'best_{key}_option'].update(option if option is not None else '')
                window[f'best_{key}_timestamp'].update(formatted_timestamp)
            else:
                window[f'best_{key}'].update('')
                window[f'best_{key}_option'].update('')
                window[f'best_{key}_timestamp'].update('')
    else:
        for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
            window[f'best_{key}'].update('')
            window[f'best_{key}_option'].update('')
            window[f'best_{key}_timestamp'].update('')

    window['delete_selectmusic'].update(disabled=False)

    window['history_timestamp'].update('')
    for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
        window[f'history_{key}'].update('')
    window['history_options'].update('')

    window['delete_selectresult'].update(disabled=True)

def display_historyresult(record, timestamp):
    if record is None:
        window['delete_selectresult'].update(disabled=True)
        return

    if not 'history' in record.keys() or not timestamp in record['history']:
        window['delete_selectresult'].update(disabled=True)
        return

    formatted_timestamp = f'{int(timestamp[0:4])}年{int(timestamp[4:6])}月{int(timestamp[6:8])}日 {timestamp[9:11]}:{timestamp[11:13]}:{timestamp[13:15]}'
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
    
    window['delete_selectresult'].update(disabled=False)

def switch_best_display():
    global best_display_mode

    index = (best_display_modes.index(best_display_mode) + 1) % len(best_display_modes)
    best_display_mode = best_display_modes[index]

    if best_display_mode == 'option':
        window['button_best_switch'].update('使用オプション >> 更新日')

    if best_display_mode == 'timestamp':
        window['button_best_switch'].update('更新日 >> 使用オプション')

    for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
        window[f'best_{key}_option'].update(visible=best_display_mode == 'option')
        window[f'best_{key}_timestamp'].update(visible=best_display_mode == 'timestamp')

def switch_textcolor(target: sg.Text, highlight: bool=False):
    if highlight:
        target.update(text_color=textcolor_highlight)
    else:
        target.update(text_color=textcolor_shadow)

def set_search_condition(playmode, difficulty, musicname):
    window['category_versions'].update('ALL')
    window['search_music'].update(musicname)

    if playmode == 'SP':
        window['play_mode_sp'].update(True)
    if playmode == 'DP':
        window['play_mode_dp'].update(True)
    
    window['difficulty'].update(difficulty)

    window['music_candidates'].update([musicname], set_to_index=[0])

def switch_resultsbuttons(enabled: bool):
    window['button_save_results'].update(disabled=not enabled)
    window['button_filter_results'].update(disabled=not enabled)
    window['button_post_results'].update(disabled=not enabled)
    window['button_upload_results'].update(disabled=not enabled)
