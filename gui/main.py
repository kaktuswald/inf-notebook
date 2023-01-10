import PySimpleGUI as sg
import io
from PIL import Image

from .static import title,icon_path,background_color
from record import Record

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
                num_rows=30,
                justification='center',
                enable_events=True,
                background_color=background_color
            )]
        ], pad=0, background_color=background_color),
        sg.Tab('曲検索', [
            [
                sg.Radio('SP', group_id='play_mode', key='play_mode_sp', enable_events=True, background_color=background_color),
                sg.Radio('DP', group_id='play_mode', key='play_mode_dp', enable_events=True, background_color=background_color)
            ],
            [
                sg.Radio('BEGINNER', group_id='difficulty', key='difficulty_beginner', enable_events=True, background_color=background_color),
                sg.Radio('LEGGENDARIA', group_id='difficulty', key='difficulty_leggendaria', enable_events=True, background_color=background_color)
            ],
            [
                sg.Radio('NORMAL', group_id='difficulty', key='difficulty_normal', enable_events=True, background_color=background_color),
                sg.Radio('HYPER', group_id='difficulty', key='difficulty_hyper', enable_events=True, background_color=background_color),
                sg.Radio('ANOTHER', group_id='difficulty', key='difficulty_another', enable_events=True, background_color=background_color)
            ],
            [
                sg.Text('曲名(4文字以上)', background_color=background_color),
                sg.Input(key='search_music', size=(20,1), enable_events=True)
            ],
            [
                sg.Listbox([], key='music_candidates', size=(40,15), enable_events=True)
            ],
            [
                sg.Text('最終プレイ', size=(11, 1)),
                sg.Text(key='latest', size=(12, 1), background_color=background_color)
            ],
            [
                sg.Text('クリアタイプ', size=(11, 1)),
                sg.Text(key='clear_type', size=(6, 1), background_color=background_color),
                sg.Text(key='clear_type_timestamp', size=(12, 1), background_color=background_color, text_color='#dddddd')
            ],
            [
                sg.Text('DJレベル', size=(11, 1)),
                sg.Text(key='dj_level', size=(6, 1), background_color=background_color),
                sg.Text(key='dj_level_timestamp', size=(12, 1), background_color=background_color, text_color='#dddddd')
            ],
            [
                sg.Text('スコア', size=(11, 1)),
                sg.Text(key='score', size=(6, 1), background_color=background_color),
                sg.Text(key='score_timestamp', size=(12, 1), background_color=background_color, text_color='#dddddd')
            ],
            [
                sg.Text('ミスカウント', size=(11, 1)),
                sg.Text(key='miss_count', size=(6, 1), background_color=background_color),
                sg.Text(key='miss_count_timestamp', size=(12, 1), background_color=background_color, text_color='#dddddd')
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
                    sg.Text('画像表示スケール', background_color=background_color),
                    sg.Combo(scales, key='scale', default_value='1/2', readonly=True)
                ],
                [
                    sg.Column([
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
                            sg.Button('ファイルに保存する', key='button_save'),
                            sg.Button('ライバルを隠して保存する', key='button_save_filtered')
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

def display_image(image):
    scale = window['scale'].get()
    if scale == '1/2':
        image = image.resize((image.width // 2, image.height // 2))
    if scale == '1/4':
        image = image.resize((image.width // 3, image.height // 3))
    
    bytes = io.BytesIO()
    image.save(bytes, format='PNG')

    window['screenshot'].update(size=image.size, data=bytes.getvalue())

def switch_table(display_music):
    if not display_music:
        displaycolumns = ['日時', 'M', 'CT', 'DL', 'SC', 'MC']
    else:
        displaycolumns = ['曲名', 'M', 'CT', 'DL', 'SC', 'MC']

    window['table_results'].Widget.configure(displaycolumns=displaycolumns)

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

    difficulty = None
    if window['difficulty_normal'].get():
        difficulty = 'NORMAL'
    if window['difficulty_hyper'].get():
        difficulty = 'HYPER'
    if window['difficulty_another'].get():
        difficulty = 'ANOTHER'
    if window['difficulty_leggendaria'].get():
        difficulty = 'LEGGENDARIA'
    if difficulty is None:
        return

    target = record.get(play_mode, difficulty)
    if target is None:
        window['latest'].update('')
        for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
            window[key].update('')
            window[f'{key}_timestamp'].update('')
        return

    timestamp = target['latest']['timestamp']
    timestamp = f'{int(timestamp[0:4])}年{int(timestamp[4:6])}月{int(timestamp[6:8])}日'
    window['latest'].update(timestamp)
    for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
        value = target['best'][key]['value']
        timestamp = target['best'][key]['timestamp']
        timestamp = f'{int(timestamp[0:4])}年{int(timestamp[4:6])}月{int(timestamp[6:8])}日'
        window[key].update(value)
        window[f'{key}_timestamp'].update(timestamp)
