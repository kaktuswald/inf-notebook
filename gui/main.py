import PySimpleGUI as sg
import io

from .static import title,icon_path

scales = ['1/1', '1/2', '1/4']

def layout_main(setting):
    column_headers = ['ファイル名', 'CT', 'DL', 'SC', 'MC']
    column_widths = [16, 3, 3, 3, 3]

    return [
        [
            sg.Column([
                [
                    sg.Text('Ctrl+F10でスクリーンショットを保存', visible=setting.manage),
                    sg.Checkbox('スクリーンショットを常時表示する', key='check_display_screenshot', visible=setting.manage, enable_events=True)
                ],
                [
                    sg.InputText(key='text_file_path', visible=setting.manage, size=(80, 1), enable_events=True),
                    sg.FileBrowse("ファイルを開く", target="text_file_path", visible=setting.manage)
                ],
                [
                    sg.Text('画像表示スケール'),
                    sg.Combo(scales, key='scale', default_value='1/2', readonly=True)
                ],
                [
                    sg.Column([
                        [sg.Checkbox('保存されたリザルトを都度表示する', key='check_display_saved_result', default=setting.display_saved_result, enable_events=True)],
                        [sg.Checkbox('更新があるときのみリザルトを保存する', key='check_save_newrecord_only', default=setting.save_newrecord_only, enable_events=True)],
                        [sg.Image(key='screenshot', size=(640, 360))],
                        [sg.Button('ライバルを隠して別に保存する', key='button_filter')]
                    ]),
                    sg.Table(
                        [],
                        key='table_results',
                        headings=column_headers,
                        auto_size_columns=False,
                        vertical_scroll_only=True,
                        col_widths=column_widths,
                        num_rows=26,
                        justification='center',
                        enable_events=True
                    ),
                ]
            ],pad=0),
            sg.Output(key='output', size=(30, 32), visible=setting.manage)
        ]
    ]

def generate_window(setting):
    global window

    window = sg.Window(
        title,
        layout_main(setting),
        icon=icon_path,
        grab_anywhere=True,
        return_keyboard_events=True,
        resizable=False,
        finalize=True,
        enable_close_attempted_event=True
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
