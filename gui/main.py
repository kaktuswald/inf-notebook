import PySimpleGUI as sg
import io
import os
from PIL import Image

from define import define
from .static import title,icon_path,background_color,background_color_label
from record import Record,get_recode_musics
from result import results_basepath

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

    tabs = [[
        sg.Tab('今日のリザルト', [
            [sg.Table(
                [],
                key='table_results',
                headings=column_headers,
                auto_size_columns=False,
                vertical_scroll_only=True,
                col_widths=column_widths,
                visible_column_map=column_visibles,
                num_rows=26,
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
                        sg.Listbox([], key='music_candidates', size=(18,13), enable_events=True),
                        sg.Listbox([], key='history', size=(15,13), enable_events=True)
                    ]
                ], pad=0, background_color=background_color)
            ],
            [
                sg.Text('最終プレイ', size=(11, 1), background_color=background_color_label),
                sg.Text(key='latest', size=(13, 1), background_color=background_color)
            ],
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
        ], pad=0, background_color=background_color)
    ]]

    return [
        [
            sg.Column([
                [
                    sg.Text('Ctrl+F10でスクリーンショットを保存', visible=setting.manage, background_color=background_color),
                    sg.Checkbox('スクリーンショットを常時表示する', key='check_display_screenshot', visible=setting.manage, enable_events=True, background_color=background_color)
                ],
                [
                    sg.InputText(key='text_file_path', visible=setting.manage, size=(80, 1), enable_events=True),
                    sg.FileBrowse("ファイルを開く", target="text_file_path", visible=setting.manage)
                ],
                [
                    sg.Column([
                        [
                            sg.Text('画像表示スケール', background_color=background_color),
                            sg.Combo(scales, key='scale', default_value='1/2', readonly=True),
                            sg.Text('INFINITASを見つけました', key='positioned', background_color=background_color, font=('Arial', 10, 'bold'), text_color='#f0fc80', visible=False)
                        ],
                        [
                            sg.Column([
                                [sg.Checkbox('更新があるときのみリザルトを記録する', key='check_newrecord_only', default=setting.newrecord_only, enable_events=True, background_color=background_color)],
                                [sg.Checkbox('自動で画像をファイルに保存する', key='check_autosave', default=setting.autosave, enable_events=True, background_color=background_color)],
                                [sg.Checkbox('自動でライバルを隠した画像をファイルに保存する', key='check_autosave_filtered', default=setting.autosave_filtered, enable_events=True, background_color=background_color)]
                            ], pad=0, background_color=background_color, vertical_alignment='top'),
                            sg.Column([
                                [sg.Checkbox('リザルトを都度表示する', key='check_display_result', default=setting.display_result, enable_events=True, background_color=background_color)],
                                [sg.Checkbox('曲名を表示する(試験運用)', key='check_display_music', default=setting.display_music, enable_events=True, background_color=background_color)]
                            ], pad=0, background_color=background_color, vertical_alignment='top')
                        ],
                        [sg.Image(key='screenshot', size=(640, 360), background_color=background_color)],
                        [
                            sg.Button('ファイルに保存する', key='button_save', disabled=True),
                            sg.Button('ライバルを隠して保存する', key='button_save_filtered', disabled=True),
                            sg.Checkbox('必ずアップロードする', key='force_upload', visible=setting.manage, background_color=background_color)
                        ]
                    ], pad=0, background_color=background_color),
                    sg.TabGroup(tabs, pad=0, background_color=background_color, tab_background_color=background_color, selected_background_color='#245d18')
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
            u'画像処理の精度向上のために大量のリザルト画像を欲しています。',
            u'リザルト画像を上画像のように切り取ってクラウドにアップロードします。',
            u'もちろん、他の目的に使用することはしません。'
            u'\n',
            u'実現できるかどうかはわかりませんが、',
            u'曲名を含めてあらゆる情報を画像から抽出して',
            u'過去のリザルトの検索などできるようにしたいと考えています。'
        ]),
        title=u'おねがい',
        image=image,
        icon=icon_path
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
        size=(60, 6)
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

def display_image(image, savable=False):
    subsample = int(window['scale'].get().split('/')[1])
    
    if image is not None:
        bytes = io.BytesIO()
        image.save(bytes, format='PNG')
        window['screenshot'].update(data=bytes.getvalue(), subsample=subsample, visible=True)
    else:
        window['screenshot'].update(visible=False)

    window['button_save'].update(disabled=not savable)
    window['button_save_filtered'].update(disabled=not savable)

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

def select_music():
    selected = window['music_candidates'].get()
    if len(selected) == 0:
        return

    music = window['music_candidates'].get()[0]
    record = Record(music)
    if record is None:
        return
    
    play_mode = None
    if window['play_mode_sp'].get():
        play_mode = 'SP'
    if window['play_mode_dp'].get():
        play_mode = 'DP'
    if play_mode is None:
        return

    difficulty = window['difficulty'].get()
    if difficulty == '':
        return

    target = record.get(play_mode, difficulty)
    if target is None:
        display_image(None)
        window['history'].update([])
        window['latest'].update('')
        for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
            window[key].update('')
            window[f'{key}_timestamp'].update('')
        return

    latest_timestamp = target['latest']['timestamp']
    formatted_timestamp = f'{int(latest_timestamp[0:4])}年{int(latest_timestamp[4:6])}月{int(latest_timestamp[6:8])}日'
    window['latest'].update(formatted_timestamp)

    window['history'].update([*reversed(target['timestamps'])])

    if 'best' in target.keys():
        for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
            value = target['best'][key]['value']
            timestamp = target['best'][key]['timestamp']
            timestamp = f'{int(timestamp[0:4])}年{int(timestamp[4:6])}月{int(timestamp[6:8])}日'
            window[key].update(value if value is not None else '')
            window[f'{key}_timestamp'].update(timestamp)
    else:
        for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
            window[key].update('')
            window[f'{key}_timestamp'].update('')
    
    filepath = os.path.join(results_basepath, f'{latest_timestamp}.jpg')
    if os.path.exists(filepath):
        image = Image.open(filepath)
        display_image(image)
    else:
        display_image(None)

def select_history():
    selected = window['history'].get()
    if len(selected) == 0:
        return

    timestamp = selected[0]
    filepath = os.path.join(results_basepath, f'{timestamp}.jpg')
    if os.path.exists(filepath):
        image = Image.open(filepath)
        display_image(image)
    else:
        display_image(None)
