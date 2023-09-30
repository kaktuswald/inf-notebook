import PySimpleGUI as sg
import io
from PIL import Image
import gui.main as gui
from os.path import exists

from .static import title,icon_path,background_color,background_color_label

icon_image = Image.open(icon_path)
resized_icon = icon_image.resize((32, 32))
icon_bytes = io.BytesIO()
resized_icon.save(icon_bytes, format='PNG')

background_dark = '#328062'

def open_setting(setting):
    layout = [
        [
            sg.Column([
                [sg.Text('リザルト記録', background_color=background_color_label)],
                [
                    sg.Text('', size=(2, 1), background_color=background_dark),
                    sg.Checkbox('更新があるときのみリザルトを記録する', key='check_newrecord_only', default=setting.newrecord_only, background_color=background_dark)
                ],
                [
                    sg.Text('', size=(2, 1), background_color=background_dark),
                    sg.Checkbox('記録したときに音を出す', key='check_play_sound', default=setting.play_sound, background_color=background_dark)
                ],
                [
                    sg.Text('', size=(2, 1), background_color=background_dark),
                    sg.Checkbox('最近のリザルトに曲名を表示する', key='check_display_music', default=setting.display_music, background_color=background_dark),
                ],
                [sg.Text('リザルト画像の保存', background_color=background_color_label)],
                [
                    sg.Text('', size=(2, 1), background_color=background_dark),
                    sg.Checkbox('自動で画像をファイルに保存する', key='check_autosave', default=setting.autosave, background_color=background_dark)
                ],
                [
                    sg.Text('', size=(2, 1), background_color=background_dark),
                    sg.Checkbox('自動でライバルを隠した画像をファイルに保存する', key='check_autosave_filtered', default=setting.autosave_filtered, background_color=background_dark)
                ],
                [
                    sg.Text('', size=(2, 1), background_color=background_dark),
                    sg.Checkbox('ファイル名の後尾に曲名をつける', key='check_savefilemusicname_right', default=setting.savefilemusicname_right, background_color=background_dark)
                ],
                [sg.Text('リザルト画像の表示', background_color=background_color_label)],
                [
                    sg.Text('', size=(2, 1), background_color=background_dark),
                    sg.Checkbox('最新の記録したリザルト画像を表示する', key='check_display_result', default=setting.display_result, background_color=background_dark)
                ],
                [sg.Text('画像の保存先のパス', background_color=background_color_label)],
                [
                    sg.Text('', size=(2, 1), background_color=background_dark),
                    sg.Input(setting.imagesave_path, key='imagesave_path', size=(50, 1)),
                    sg.Button('...', key='button_browse'),
                ],
                [sg.Text('リザルト画像の収集', background_color=background_color_label)],
                [
                    sg.Text('', size=(2, 1), background_color=background_dark),
                    sg.Checkbox('画像の収集に協力する', key='check_data_collection', default=setting.data_collection, background_color=background_dark)
                ],
            ], pad=0, size=(460, 300), background_color=background_dark, scrollable=True, vertical_scroll_only=True)
        ],
        [
            sg.Button('保存', key='button_save', size=(10, 1)),
            sg.Button('閉じる', key='button_close', size=(10, 1))
        ]
    ]

    window = sg.Window(
        f'{title} (設定)',
        layout,
        icon=icon_path,
        grab_anywhere=True,
        return_keyboard_events=True,
        resizable=False,
        finalize=True,
        enable_close_attempted_event=True,
        background_color=background_color,
        modal=True
    )

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT, 'button_close'):
            break

        if event == 'button_browse':
            result = sg.popup_get_folder('', no_window=True)
            path = result.replace('/', '\\')
            if exists(path):
                window['imagesave_path'].update(path)
        if event == 'button_save':
            setting.display_result = values['check_display_result']
            setting.newrecord_only = values['check_newrecord_only']
            setting.autosave = values['check_autosave']
            setting.autosave_filtered = values['check_autosave_filtered']
            setting.display_music = values['check_display_music']
            setting.play_sound = values['check_play_sound']
            setting.savefilemusicname_right = values['check_savefilemusicname_right']
            setting.imagesave_path = values['imagesave_path']
            setting.data_collection = values['check_data_collection']
            setting.save()
            gui.switch_table(setting.display_music)

    window.close()

    return
