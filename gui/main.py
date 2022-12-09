import PySimpleGUI as sg

scales = ['1/1', '1/2', '1/4']

def layout_main(setting):
    column_headers = ['ファイル名', 'CT', 'DL', 'SC', 'MC']
    column_widths = [16, 3, 3, 3, 3]

    return [
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
                vertical_scroll_only=False,
                col_widths=column_widths,
                num_rows=26,
                justification='center',
                enable_events=True
            ),
        ]
    ]
