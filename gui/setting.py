import PySimpleGUI as sg
import io
from PIL import Image
import gui.main as gui
from os.path import exists

from .static import title,icon_path,background_color,background_color_label,selected_background_color
from .general import get_imagevalue,question
from .main import display_image
from define import define
from image import generateimage_summary

icon_image = Image.open(icon_path)
resized_icon = icon_image.resize((32, 32))
icon_bytes = io.BytesIO()
resized_icon.save(icon_bytes, format='PNG')

background_dark = '#328062'

summarytypes = {'cleartypes': 'clear_types', 'djlevels': 'dj_levels'}
summarytargetlevels = ['8', '9', '10', '11', '12']
summarytargetcleartypes = ['CLEAR', 'H-CLEAR', 'EXH-CLEAR', 'F-COMBO']
summarytargetdjlevels = ['A', 'AA', 'AAA']

def open_setting(setting):
    tab_general = [[
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
                sg.Checkbox('ライバルのフィルターを最小限にする', key='check_filter_compact', default=setting.filter_compact, background_color=background_dark)
            ],
            [
                sg.Text('', size=(2, 1), background_color=background_dark),
                sg.Checkbox('ファイル名の後尾に曲名をつける', key='check_savefilemusicname_right', default=setting.savefilemusicname_right, background_color=background_dark)
            ],
            [sg.Text('ショートカットキー', background_color=background_color_label)],
            [
                sg.Text('', size=(2, 1), background_color=background_dark),
                sg.Text('統計データ表示', size=(20, 1), background_color=background_dark),
                sg.Input(setting.hotkeys['display_summaryimage'], size=(12, 1), key='hotkey_display_summaryimage')
            ],
            [
                sg.Text('', size=(2, 1), background_color=background_dark),
                sg.Text('スクリーンショット', size=(20, 1), background_color=background_dark),
                sg.Input(setting.hotkeys['active_screenshot'], size=(12, 1), key='hotkey_active_screenshot'),
            ],
            [
                sg.Text('', size=(2, 1), background_color=background_dark),
                sg.Text('選曲画面のアップロード', size=(20, 1), background_color=background_dark),
                sg.Input(setting.hotkeys['upload_musicselect'], size=(12, 1), key='hotkey_upload_musicselect')
            ],
            [sg.Text('統計データの曲数', background_color=background_color_label)],
            [
                sg.Text('', size=(2, 1), background_color=background_dark),
                sg.Radio('達成している曲数をカウントする', group_id='summary_countmethod', key='summary_countmethod_sum', background_color=background_dark, enable_events=True, default=not setting.summary_countmethod_only),
                sg.Radio('対象の曲数のみをカウントする', group_id='summary_countmethod', key='summary_countmethod_only', background_color=background_dark, enable_events=True, default=setting.summary_countmethod_only)
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
        ], pad=0, size=(640, 300), background_color=background_dark, scrollable=True, vertical_scroll_only=True)
    ]]
    
    controls = []
    for playmode in define.value_list['play_modes']:
        controls_levels = []
        for level in summarytargetlevels:
            controls_levels.append([
                sg.Text(level, size=(2,1), background_color=background_color_label),
                sg.Column([
                    [
                        *[sg.Checkbox(key, default=key in setting.summaries[playmode][level]['cleartypes'], key=f'check_summary_{playmode}_{level}_{key}', enable_events=True, background_color=background_color) for key in summarytargetcleartypes],
                        sg.Text('', background_color=background_color_label),
                        *[sg.Checkbox(key, default=key in setting.summaries[playmode][level]['djlevels'], key=f'check_summary_{playmode}_{level}_{key}', enable_events=True, background_color=background_color) for key in summarytargetdjlevels]
                    ],
                ], pad=2, background_color=background_color)
            ])
        controls.append([
            sg.Text(playmode, background_color=background_dark),
            sg.Column(controls_levels, pad=2, background_color=background_color_label)
        ])

    tab_summary = [[
        sg.Column([
            [sg.Text('エクスポートされたCSVファイルから、チェックした成績を達成している曲の数を表示します。', background_color=background_dark)],
            [sg.Text('リザルト手帳の起動時に表示するほか、Alt+F9で再表示します。', background_color=background_dark)],
            [sg.Text('表示したデータはexportフォルダに画像保存します。', background_color=background_dark)],
            *controls
        ], pad=0, size=(640, 300), background_color=background_dark, scrollable=True, vertical_scroll_only=True)
    ]]

    layout = [[
        sg.TabGroup([[
            sg.Tab('一般', tab_general, pad=0, background_color=background_color),
            sg.Tab('統計', tab_summary, pad=0, background_color=background_color)
        ]], pad=0, background_color=background_color, tab_background_color=background_color, selected_background_color=selected_background_color)
    ],
    [
        sg.Button('保存', key='button_save', size=(10, 1)),
        sg.Button('閉じる', key='button_close', size=(10, 1))
    ]]

    changed_summaries = False
    saved_summaries = False

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
        if 'check_summary' in event or 'summary_countmethod' in event:
            changed_summaries = True
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
            setting.summaries = set_summarysetting(window)
            setting.hotkeys = {
                'display_summaryimage': values['hotkey_display_summaryimage'],
                'active_screenshot': values['hotkey_active_screenshot'],
                'upload_musicselect': values['hotkey_upload_musicselect'],
            }
            setting.summary_countmethod_only = values['summary_countmethod_only']
            setting.filter_compact = values['check_filter_compact']
            setting.save()
            gui.switch_table(setting.display_music)
            if changed_summaries:
                saved_summaries = True

    window.close()

    return saved_summaries

def set_summarysetting(window):
    summaries = {}
    for playmode in define.value_list['play_modes']:
        summaries[playmode] = {}
        for level in summarytargetlevels:
            summaries[playmode][level] = {}
            for summarytype_a, summarytype_b in summarytypes.items():
                summaries[playmode][level][summarytype_a] = []
                for key in define.value_list[summarytype_b]:
                    keyname = f'check_summary_{playmode}_{level}_{key}'
                    if keyname in window.AllKeysDict.keys() and window[keyname].get():
                        summaries[playmode][level][summarytype_a].append(key)

    return summaries
