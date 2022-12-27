import PySimpleGUI as sg
import io
from PIL import Image

from .static import title,icon_path,background_color

scales = ['1/1', '1/2', '1/4']

icon_image = Image.open(icon_path)
resized_icon = icon_image.resize((32, 32))
icon_bytes = io.BytesIO()
resized_icon.save(icon_bytes, format='PNG')

def layout_main(setting):
    column_headers = ['日時', '曲名', 'CT', 'DL', 'SC', 'MC']
    column_widths = [13, 13, 3, 3, 3, 3]

    if setting.display_music:
        column_visibles = [False, True, True, True, True, True]
    else:
        column_visibles = [True, False, True, True, True, True]

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
                    sg.Table(
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
                    ),
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
        displaycolumns = ['日時', 'CT', 'DL', 'SC', 'MC']
    else:
        displaycolumns = ['曲名', 'CT', 'DL', 'SC', 'MC']

    window['table_results'].Widget.configure(displaycolumns=displaycolumns)
