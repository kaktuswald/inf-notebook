import PySimpleGUI as sg
import io
from PIL import Image
import random
import string
from time import time

from version import version
from .static import title,icon_path,background_color,background_color2_label
from discord_webhook import default
from resources import resource
from define import define

icon_image = Image.open(icon_path)
resized_icon = icon_image.resize((32, 32))
icon_bytes = io.BytesIO()
resized_icon.save(icon_bytes, format='PNG')

def generate_randamsettingname(length: int = 4):
    characters =  [random.choice(string.ascii_uppercase) for i in range(length)]
    return ''.join(['Server', '-', *characters])

def update_musiclist(window, values):
    if values['version_select'] == 'ALL':
        targets = resource.musictable['musics'].keys()
    else:
        targets = resource.musictable['versions'][values['version_select']]
    if len(values['musicname_input']) > 0:
        window['target_musicname'].update(values=[n for n in targets if values['musicname_input'] in n])
    else:
        window['target_musicname'].update(values=targets)

def open_setting(location: tuple[int, int], name: str = None, setting: dict = default) -> tuple[str, dict]:
    if name is None:
        name = generate_randamsettingname()
    
    musiclist = [*resource.musictable['musics'].keys()]
    if setting['targetscore'] is not None:
        selected_music = setting['targetscore']['musicname']
        selected_playmode = setting['targetscore']['playmode']
        selected_difficulty = setting['targetscore']['difficulty']
    else:
        selected_music = ''
        selected_playmode = 'SP'
        selected_difficulty = 'NORMAL'
    
    layout = [
        [
            sg.Text('名称', size=(12, 1), background_color=background_color2_label),
            sg.Input(key='settingname', default_text=name, size=(80,1))
        ],
        [
            sg.Text('URL', size=(12, 1), background_color=background_color2_label),
            sg.Input(key='url', default_text=setting['url'], size=(80,1))
        ],
        [
            sg.Text('ライバル名', size=(12, 1), background_color=background_color2_label),
            sg.Radio('ぼかさない', group_id='filter', key='filter_none', default=setting['filter'] == 'none', background_color=background_color),
            sg.Radio('全体をぼかす', group_id='filter', key='filter_whole', default=setting['filter'] == 'whole', background_color=background_color),
            sg.Radio('DJ NAMEのみぼかす', group_id='filter', key='filter_compact', default=setting['filter'] == 'compact', background_color=background_color)
        ],
        [
            sg.Text('投稿対象', size=(12, 1), background_color=background_color2_label),
            sg.Radio('すべてのリザルト', group_id='postcondition', key='postcondition_all', default=setting['postcondition'] == 'all', background_color=background_color, enable_events=True),
            sg.Radio('更新したリザルト', group_id='postcondition', key='postcondition_onlyupdated', default=setting['postcondition'] == 'onlyupdated', background_color=background_color, enable_events=True),
            sg.Radio('指定の譜面', group_id='postcondition', key='postcondition_targetscore', default=setting['postcondition'] == 'targetscore', background_color=background_color, enable_events=True)
        ],
        [
            sg.Text('対象譜面', size=(12, 1), background_color=background_color2_label),
            sg.Column([
                [
                    sg.Text('絞り込み', background_color=background_color),
                    sg.Combo(['ALL', *resource.musictable['versions'].keys()], default_value='ALL', key='version_select', disabled=setting['postcondition'] != 'targetscore', readonly=True, enable_events=True),
                    sg.Input('', size=(20, 1), key='musicname_input', disabled=setting['postcondition'] != 'targetscore', enable_events=True)
                ],
                [
                    sg.Listbox(musiclist, key='target_musicname', default_values=[selected_music], disabled=setting['postcondition'] != 'targetscore', size=(55, 5), enable_events=True)
                ],
                [
                    sg.Text('選択中:', background_color=background_color),
                    sg.Text(selected_music, key='selected_musicname', background_color=background_color)
                ],
                [
                    sg.Combo(define.value_list['play_modes'], default_value=selected_playmode, key='target_playmode', disabled=setting['postcondition'] != 'targetscore', readonly=True, enable_events=True),
                    sg.Combo(define.value_list['difficulties'], default_value=selected_difficulty, key='target_difficulty', disabled=setting['postcondition'] != 'targetscore', readonly=True, enable_events=True)
                ]
            ], pad=0, background_color=background_color)
        ],
        [
            sg.Text('投稿内容', size=(12, 1), background_color=background_color2_label),
            sg.Radio('詳細', group_id='posttext', key='posttext_all', default=setting['posttext'] == 'all', background_color=background_color),
            sg.Radio('スコアのみ', group_id='posttext', key='posttext_onlyscore', default=setting['posttext'] == 'onlyscore', background_color=background_color),
            sg.Radio('ミスカウントのみ', group_id='posttext', key='posttext_onlymisscount', default=setting['posttext'] == 'onlymisscount', background_color=background_color)
        ],
        [
            sg.Text('リザルト画像', size=(12, 1), background_color=background_color2_label),
            sg.Radio('投稿する', group_id='postimage', key='postimage_yes', default=setting['postimage'] == 'yes', background_color=background_color),
            sg.Radio('投稿しない', group_id='postimage', key='postimage_no', default=setting['postimage'] == 'no', background_color=background_color)
        ],
        [
            sg.Text('', key='message', background_color=background_color, text_color='#ff0000')
        ],
        [
            sg.Button('OK', key='ok'),
            sg.Button('キャンセル', key='cancel')
        ]
    ]

    window = sg.Window(
        f'{title} ({version})',
        layout,
        icon=icon_path,
        grab_anywhere=True,
        return_keyboard_events=True,
        resizable=False,
        finalize=True,
        enable_close_attempted_event=True,
        background_color=background_color,
        relative_location=location
    )

    music_search_time = None

    try:
        while True:
            event, values = window.read(timeout=50, timeout_key='timeout')

            if event in (sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT, 'cancel'):
                window.close()
                return None, None
            
            if 'postcondition' in event:
                window['version_select'].update(disabled=event!='postcondition_targetscore')
                window['musicname_input'].update(disabled=event!='postcondition_targetscore')
                window['target_musicname'].update(disabled=event!='postcondition_targetscore')
                window['target_playmode'].update(disabled=event!='postcondition_targetscore')
                window['target_difficulty'].update(disabled=event!='postcondition_targetscore')
            if event == 'musicname_input':
                music_search_time = time() + 1
            if event == 'version_select':
                update_musiclist(window, values)
            if event == 'target_musicname':
                if len(values['target_musicname']) > 0:
                    window['selected_musicname'].update(values['target_musicname'][0])
            
            if event == 'timeout':
                if music_search_time is not None and time() > music_search_time:
                    music_search_time = None
                    update_musiclist(window, values)

            if event == 'ok':
                if len(values['settingname']) == 0:
                    window['message'].update('名称を入力してください。')
                    continue
                if len(values['settingname']) > 256:
                    window['message'].update('名称を短くしてください。')
                    continue
                if len(values['url']) == 0:
                    window['message'].update('URLを入力してください。')
                    continue
                if len(values['url']) > 256:
                    window['message'].update('URLを短くしてください。')
                    continue
                if values['postcondition_targetscore']:
                    if len(values['target_musicname']) == 0:
                        window['message'].update('対象曲を選択してください。')
                        continue
                    musicname = values['target_musicname'][0]
                    playmode = values['target_playmode']
                    difficulty = values['target_difficulty']
                    if not difficulty in resource.musictable['musics'][musicname][playmode].keys():
                        window['message'].update(f'{musicname}の{playmode}の{difficulty}はありません。')
                        continue
                    targetscore = {
                        'musicname': musicname,
                        'playmode': playmode,
                        'difficulty': difficulty
                    }
                else:
                    targetscore = None

                break
    except Exception as ex:
        print(ex)
    
    window.close()

    return (
        values['settingname'],
        {
            'url': values['url'],
            'filter': [k.replace('filter_', '') for k, v in values.items() if 'filter' in k and v][0],
            'postcondition': [k.replace('postcondition_', '') for k, v in values.items() if 'postcondition' in k and v][0],
            'targetscore': targetscore,
            'posttext': [k.replace('posttext_', '') for k, v in values.items() if 'posttext' in k and v][0],
            'postimage': [k.replace('postimage_', '') for k, v in values.items() if 'postimage' in k and v][0]
        }
    )
