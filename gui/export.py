import PySimpleGUI as sg
import io
from os.path import isfile
from PIL import Image
from pyperclip import copy
from os.path import abspath
from re import compile
import json

from define import define
from .static import title,icon_path,background_color,background_color_label,selected_background_color
from .general import message
from playdata import output,export_dirname,csssetting_filepath

icon_image = Image.open(icon_path)
resized_icon = icon_image.resize((32, 32))
icon_bytes = io.BytesIO()
resized_icon.save(icon_bytes, format='PNG')

pattern_color = compile('#[0-9a-fA-F]{6}')

graph_color_size=(15, 15)
graph_blank_size=(2, 2)

csssetting = {
    'recent': {
        'size': '46',
        'color': '#808080',
        'shadow-color': '#000000',
        'NORMAL': '#157aea',
        'HYPER': '#eaea15',
        'ANOTHER': '#ea1515',
        'BEGINNER': '#15ea25',
        'LEGGENDARIA': '#9f2020',
        'overviews': {
            'played_count': {
                'display': True,
                'color': '#c0c0ff'
            },
            'score': {
                'display': False,
                'color': '#c0c0ff'
            },
            'misscount': {
                'display': False,
                'color': '#c0c0ff'
            },
            'updated_score': {
                'display': False,
                'color': '#c0c0ff'
            },
            'updated_misscount': {
                'display': False,
                'color': '#c0c0ff'
            },
            'clear': {
                'display': False,
                'color': '#c0c0ff'
            },
            'failed': {
                'display': False,
                'color': '#c0c0ff'
            },
        }
    },
    'summary': {
        'color': '#808080',
        'shadow-color': '#000000',
        'date color': '#c0c0ff',
        'SP': {
            'checked': True,
            'difficulties': {
                'checked': ['ANOTHER'],
                'clear_types': [],
                'dj_levels': ['A', 'AA', 'AAA']
            },
            'levels': {
                'checked': [],
                'clear_types': [],
                'dj_levels': []
            }
        },
        'DP': {
            'checked': True,
            'difficulties': {
                'checked': ['ANOTHER'],
                'clear_types': [],
                'dj_levels': ['A', 'AA', 'AAA']
            },
            'levels': {
                'checked': [],
                'clear_types': [],
                'dj_levels': []
            }
        }
    }
}

def open_export(recent):
    global csssetting

    try:
        if isfile(csssetting_filepath):
            with open(csssetting_filepath) as f:
                csssetting = json.load(f)
    except:
        pass

    tab_manual = [
        [sg.Text('リザルト手帳はいくつかのファイルをexportフォルダに作成します。', background_color=background_color)],
        [
            sg.Text('exportの場所', background_color=background_color),
            sg.Input(key='exportpath', size=(60, 1)),
            sg.Button('クリップボードにコピー', key='button_copy_exportpath')
        ],
        [sg.Graph(canvas_size=graph_blank_size, graph_bottom_left=(0, 0), graph_top_right=graph_blank_size, background_color=background_color)],
        [
            sg.Column([
                [sg.Text('CSV出力', background_color=background_color_label)]
            ], pad=5, background_color=background_color_label)
        ],
        [sg.Text('「CSV出力」ボタンを押すと全プレイデータと、いくつかの統計データファイル(CSV)を作成します。', background_color=background_color)],
        [sg.Text('作られた統計データファイルはExcel等で開くことができます。', background_color=background_color)],
        [
            sg.Column([
                [sg.Text('全プレイデータ', background_color=background_color_label)]
            ], pad=5, background_color=background_color_label)
        ],
        [sg.Text('SP.csvとDP.csvは全プレイデータです。', background_color=background_color)],
        [
            sg.Column([
                [sg.Text('統計データ', background_color=background_color_label)]
            ], pad=5, background_color=background_color_label)
        ],
        [sg.Text('難易度ごとの各クリアタイプ・各DJレベルの曲数や、レベルごとの各クリアタイプ・各DJレベルの曲数を統計したファイルを作成します。', background_color=background_color)],
        [sg.Text('たとえば、SP-難易度-DJレベル.csv はSPの難易度ごとに各DJレベルの曲数を統計したデータです。', background_color=background_color)],
        [sg.Text('各行の「total」はリザルト手帳で記録済みの曲数です。', background_color=background_color)],
        [sg.Text('INFINITASに収録されている曲数とは異なるのでご注意ください。', background_color=background_color)]
    ]

    tab_obs = [
        [
            sg.Column([
                [sg.Text('OBSとは録画や配信をするためのソフトウェアです。', background_color=background_color_label)]
            ], pad=5, background_color=background_color_label)
        ],
        [sg.Text('exportフォルダに含まれる最近のデータ(recent.html)と統計データ(summary.html)は、OBSに追加することができます。', background_color=background_color)],
        [sg.Text('ソースにブラウザを追加して、ローカルファイルのチェックを入れて対象のhtmlファイルを指定してください。', background_color=background_color)],
        [
            sg.Column([
                [sg.Text('recent.html', background_color=background_color_label)]
            ], pad=5, background_color=background_color_label)
        ],
        [sg.Text('過去12時間以内のプレイ曲数と曲名が表示できます。', background_color=background_color)],
        [
            sg.Column([
                [sg.Text('summary.html', background_color=background_color_label)]
            ], pad=5, background_color=background_color_label)
        ],
        [sg.Text('CSV出力で作られた統計データファイルを表示できます。', background_color=background_color)],
        [sg.Text('デフォルトではSP,DP両方のANOTHERのA,AA,AAAの曲数を表示します。', background_color=background_color)],
        [sg.Text('表示内容を変更するときは「統計データ」タブでカスタムCSSを作成してください。', background_color=background_color)],
        [
            sg.Column([
                [sg.Text('カスタムCSS', background_color=background_color_label)]
            ], pad=5, background_color=background_color_label)
        ],
        [sg.Text('「最近のデータ」「統計データ」タブからカスタムCSSを作成できます。', background_color=background_color)],
        [sg.Text('作成されたCSSをコピーして、OBSのほうのソースのプロパティで「カスタムCSS」に貼り付けてください。', background_color=background_color)]
    ]

    tab_recent = [
        [
            sg.Text('文字サイズ', size=(10, 1), justification='right', background_color=background_color),
            sg.Input(csssetting['recent']['size'], size=(4, 1), key='recent size', enable_events=True),
            sg.Text('px', background_color=background_color),
            sg.Text('文字色', size=(10, 1), justification='right', background_color=background_color),
            sg.Input(csssetting['recent']['color'], size=(9, 1), key='recent color', enable_events=True),
            sg.Graph(key='graph recent color', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#808080'),
            sg.Text('影色', size=(10, 1), justification='right', background_color=background_color),
            sg.Input(csssetting['recent']['shadow-color'], size=(9, 1), key='recent shadow-color', enable_events=True),
            sg.Graph(key='graph recent shadow-color', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#000000')
        ],
        [
            sg.Text('NORMAL', size=(15, 1), justification='right', background_color=background_color),
            sg.Input(csssetting['recent']['NORMAL'], size=(9, 1), key='recent NORMAL color', enable_events=True),
            sg.Graph(key='graph recent NORMAL', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#808080'),
            sg.Text('HYPER', size=(15, 1), justification='right', background_color=background_color),
            sg.Input(csssetting['recent']['HYPER'], size=(9, 1), key='recent HYPER color', enable_events=True),
            sg.Graph(key='graph recent HYPER', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#808080'),
            sg.Text('ANOTHER', size=(15, 1), justification='right', background_color=background_color),
            sg.Input(csssetting['recent']['ANOTHER'], size=(9, 1), key='recent ANOTHER color', enable_events=True),
            sg.Graph(key='graph recent ANOTHER', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#808080'),
        ],
        [
            sg.Text('BEGINNER', size=(15, 1), justification='right', background_color=background_color),
            sg.Input(csssetting['recent']['BEGINNER'], size=(9, 1), key='recent BEGINNER color', enable_events=True),
            sg.Graph(key='graph recent BEGINNER', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#808080'),
            sg.Text('LEGGENDARIA', size=(15, 1), justification='right', background_color=background_color),
            sg.Input(csssetting['recent']['LEGGENDARIA'], size=(9, 1), key='recent LEGGENDARIA color', enable_events=True),
            sg.Graph(key='graph recent LEGGENDARIA', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#808080')
        ],
        [
            sg.Column([
                [
                    sg.Text('プレイ曲数', background_color=background_color_label, size=(26, None), justification='right'),
                    sg.Checkbox('表示する', key='recent played_count display', default=csssetting['recent']['overviews']['played_count']['display'], enable_events=True, background_color=background_color_label)
                ]
            ], pad=5, background_color=background_color_label),
            sg.Text('文字色', justification='right', background_color=background_color),
            sg.Input(csssetting['recent']['overviews']['played_count']['color'], size=(9, 1), key='recent played_count color', enable_events=True),
            sg.Graph(key='graph recent played_count color', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#c0c0ff'),
        ],
        [
            sg.Column([
                [
                    sg.Text('スコアの合計', background_color=background_color_label, size=(26, None), justification='right'),
                    sg.Checkbox('表示する', key='recent score display', default=csssetting['recent']['overviews']['score']['display'], enable_events=True, background_color=background_color_label)
                ]
            ], pad=5, background_color=background_color_label),
            sg.Text('文字色', justification='right', background_color=background_color),
            sg.Input(csssetting['recent']['overviews']['score']['color'], size=(9, 1), key='recent score color', enable_events=True),
            sg.Graph(key='graph recent score color', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#c0c0ff'),
        ],
        [
            sg.Column([
                [
                    sg.Text('ミスカウントの合計', background_color=background_color_label, size=(26, None), justification='right'),
                    sg.Checkbox('表示する', key='recent misscount display', default=csssetting['recent']['overviews']['misscount']['display'], enable_events=True, background_color=background_color_label)
                ]
            ], pad=5, background_color=background_color_label),
            sg.Text('文字色', justification='right', background_color=background_color),
            sg.Input(csssetting['recent']['overviews']['misscount']['color'], size=(9, 1), key='recent misscount color', enable_events=True),
            sg.Graph(key='graph recent misscount color', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#c0c0ff'),
        ],
        [
            sg.Column([
                [
                    sg.Text('更新したスコアの合計', background_color=background_color_label, size=(26, None), justification='right'),
                    sg.Checkbox('表示する', key='recent updated_score display', default=csssetting['recent']['overviews']['updated_score']['display'], enable_events=True, background_color=background_color_label)
                ]
            ], pad=5, background_color=background_color_label),
            sg.Text('文字色', justification='right', background_color=background_color),
            sg.Input(csssetting['recent']['overviews']['updated_score']['color'], size=(9, 1), key='recent updated_score color', enable_events=True),
            sg.Graph(key='graph recent updated_score color', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#c0c0ff'),
        ],
        [
            sg.Column([
                [
                    sg.Text('更新したミスカウントの合計', background_color=background_color_label, size=(26, None), justification='right'),
                    sg.Checkbox('表示する', key='recent updated_misscount display', default=csssetting['recent']['overviews']['updated_misscount']['display'], enable_events=True, background_color=background_color_label)
                ]
            ], pad=5, background_color=background_color_label),
            sg.Text('文字色', justification='right', background_color=background_color),
            sg.Input(csssetting['recent']['overviews']['updated_misscount']['color'], size=(9, 1), key='recent updated_misscount color', enable_events=True),
            sg.Graph(key='graph recent updated_misscount color', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#c0c0ff'),
        ],
        [
            sg.Column([
                [
                    sg.Text('クリアの回数', background_color=background_color_label, size=(26, None), justification='right'),
                    sg.Checkbox('表示する', key='recent clear display', default=csssetting['recent']['overviews']['clear']['display'], enable_events=True, background_color=background_color_label)
                ]
            ], pad=5, background_color=background_color_label),
            sg.Text('文字色', justification='right', background_color=background_color),
            sg.Input(csssetting['recent']['overviews']['clear']['color'], size=(9, 1), key='recent clear color', enable_events=True),
            sg.Graph(key='graph recent clear color', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#c0c0ff'),
        ],
        [
            sg.Column([
                [
                    sg.Text('FAILEDの回数', background_color=background_color_label, size=(26, None), justification='right'),
                    sg.Checkbox('表示する', key='recent failed display', default=csssetting['recent']['overviews']['failed']['display'], enable_events=True, background_color=background_color_label)
                ]
            ], pad=5, background_color=background_color_label),
            sg.Text('文字色', justification='right', background_color=background_color),
            sg.Input(csssetting['recent']['overviews']['failed']['color'], size=(9, 1), key='recent failed color', enable_events=True),
            sg.Graph(key='graph recent failed color', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#c0c0ff'),
        ]
    ]

    tab_summary = [
        [
            sg.Text('文字色', size=(8, 1), justification='right', background_color=background_color),
            sg.Input(csssetting['summary']['color'], size=(9, 1), key='summary color', enable_events=True),
            sg.Graph(key='graph summary color', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#808080'),
            sg.Text('影色', size=(6, 1), justification='right', background_color=background_color),
            sg.Input(csssetting['summary']['shadow-color'], size=(9, 1), key='summary shadow-color', enable_events=True),
            sg.Graph(key='graph summary shadow-color', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#000000'),
            sg.Text('日時の文字色', size=(15, 1), justification='right', background_color=background_color),
            sg.Input(csssetting['summary']['date color'], size=(9, 1), key='summary date color', enable_events=True),
            sg.Graph(key='graph summary date color', canvas_size=graph_color_size, graph_bottom_left=(0, 0), graph_top_right=graph_color_size, background_color='#c0c0ff')
        ],
        [
            sg.Checkbox('SP', key='SP', default=csssetting['summary']['SP']['checked'], enable_events=True, background_color=background_color),
            sg.Column([
                [
                    *[sg.Checkbox(value, default=value in csssetting['summary']['SP']['difficulties']['checked'], key=f'check SP {value}', enable_events=True, background_color=background_color_label) for value in define.value_list['difficulties']],
                ],
                [
                    sg.Column([
                        [
                            *[sg.Checkbox(value, default=value in csssetting['summary']['SP']['difficulties']['clear_types'], key=f'check SP difficulty {value}', enable_events=True, background_color=background_color) for value in define.value_list['clear_types']]
                        ],
                        [
                            *[sg.Checkbox(value, default=value in csssetting['summary']['SP']['difficulties']['dj_levels'], key=f'check SP difficulty {value}', enable_events=True, background_color=background_color) for value in define.value_list['dj_levels']]
                        ],
                    ], pad=2, background_color=background_color)
                ],
                [
                    *[sg.Checkbox(value, default=value in csssetting['summary']['SP']['levels']['checked'], key=f'check SP {value}', enable_events=True, background_color=background_color_label) for value in define.value_list['levels']]
                ],
                [
                    sg.Column([
                        [
                            *[sg.Checkbox(value, default=value in csssetting['summary']['SP']['levels']['clear_types'], key=f'check SP level {value}', enable_events=True, background_color=background_color) for value in define.value_list['clear_types']]
                        ],
                        [
                            *[sg.Checkbox(value, default=value in csssetting['summary']['SP']['levels']['dj_levels'], key=f'check SP level {value}', enable_events=True, background_color=background_color) for value in define.value_list['dj_levels']]
                        ],
                    ], pad=2, background_color=background_color)
                ],
            ], pad=2, background_color=background_color_label)
        ],
        [
            sg.Checkbox('DP', key='DP', default=csssetting['summary']['DP']['checked'], enable_events=True, background_color=background_color),
            sg.Column([
                [
                    *[sg.Checkbox(value, default=value in csssetting['summary']['DP']['difficulties']['checked'], key=f'check DP {value}', enable_events=True, background_color=background_color_label) for value in define.value_list['difficulties']],
                ],
                [
                    sg.Column([
                        [
                            *[sg.Checkbox(value, default=value in csssetting['summary']['DP']['difficulties']['clear_types'], key=f'check DP difficulty {value}', enable_events=True, background_color=background_color) for value in define.value_list['clear_types']]
                        ],
                        [
                            *[sg.Checkbox(value, default=value in csssetting['summary']['DP']['difficulties']['dj_levels'], key=f'check DP difficulty {value}', enable_events=True, background_color=background_color) for value in define.value_list['dj_levels']]
                        ],
                    ], pad=2, background_color=background_color)
                ],
                [
                    *[sg.Checkbox(value, default=value in csssetting['summary']['DP']['levels']['checked'], key=f'check DP {value}', enable_events=True, background_color=background_color_label) for value in define.value_list['levels']]
                ],
                [
                    sg.Column([
                        [
                            *[sg.Checkbox(value, default=value in csssetting['summary']['DP']['levels']['clear_types'], key=f'check DP level {value}', enable_events=True, background_color=background_color) for value in define.value_list['clear_types']]
                        ],
                        [
                            *[sg.Checkbox(value, default=value in csssetting['summary']['DP']['levels']['dj_levels'], key=f'check DP level {value}', enable_events=True, background_color=background_color) for value in define.value_list['dj_levels']]
                        ],
                    ], pad=2, background_color=background_color)
                ],
            ], pad=2, background_color=background_color_label)
        ]
    ]

    layout = [
        [
            sg.TabGroup([[
                sg.Tab('マニュアル', tab_manual, pad=0, background_color=background_color),
                sg.Tab('OBSについて', tab_obs, pad=0, background_color=background_color),
                sg.Tab('最近のデータ', tab_recent, pad=0, background_color=background_color),
                sg.Tab('統計データ', tab_summary, pad=0, background_color=background_color)
            ]], pad=0, background_color=background_color, tab_background_color=background_color, selected_background_color=selected_background_color)
        ],
        [
        ],

        [
            sg.Multiline(key='css', size=(60, 6)),
            sg.Column([
                [
                    sg.Button('CSV出力', key='button_output_csv'),
                    sg.Button('最近のデータのリセット', key='button_clear_recent')
                ],
                [sg.Button('←CSSをクリップボードにコピー', key='button_copy_css')],
                [sg.Button('閉じる', key='button_close')]
            ], pad=0, background_color=background_color, vertical_alignment='bottom')
        ]
    ]

    window = sg.Window(
        f'{title} (エクスポート)',
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

    generate_recent_css(window)
    window['exportpath'].update(abspath(export_dirname))

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT, 'button_close'):
            break
        if 'recent' in event:
            generate_recent_css(window)
        if 'summary' in event:
            generate_summary_css(window)
        if event in define.value_list['play_modes']:
            change_checkstatus_from_playside(window, event)
            generate_summary_css(window)
        if 'check' in event:
            generate_summary_css(window)
        if event == 'button_output_csv':
            output()
            message('完了', '出力が完了しました。')
        if event == 'button_clear_recent':
            recent.clear()
        if event == 'button_copy_css':
            copy(values['css'])
        if event == 'button_copy_exportpath':
            copy(values['exportpath'])

    window.close()

    return

def change_checkstatus_from_playside(window, play_mode):
    value = window[play_mode].get()
    for difficulty in define.value_list['difficulties']:
        window[f'check {play_mode} {difficulty}'].update(disabled=not value)
    for level in define.value_list['levels']:
        window[f'check {play_mode} {level}'].update(disabled=not value)
    for clear_type in define.value_list['clear_types']:
        window[f'check {play_mode} difficulty {clear_type}'].update(disabled=not value)
        window[f'check {play_mode} level {clear_type}'].update(disabled=not value)
    for dj_level in define.value_list['dj_levels']:
        window[f'check {play_mode} difficulty {dj_level}'].update(disabled=not value)
        window[f'check {play_mode} level {dj_level}'].update(disabled=not value)

def generate_recent_css(window):
    css = []

    css.append('body {')
    size = window[f'recent size'].get()
    if str.isdecimal(size):
        css.append(f'  font-size: {size}px;')
        csssetting['recent']['size'] = size
    color = window[f'recent color'].get()
    if pattern_color.fullmatch(color) is not None:
        window[f'graph recent color'].update(background_color=color)
        css.append(f'  color: {color};')
        csssetting['recent']['color'] = color
    shadow_color = window[f'recent shadow-color'].get()
    if pattern_color.fullmatch(shadow_color) is not None:
        window[f'graph recent shadow-color'].update(shadow_color)
        shadows = ['1px 1px', '-1px 1px', '1px -1px', '-1px -1px']
        shadow_value = [f'{shadow} 0 {shadow_color}' for shadow in shadows]
        css.append(f"  text-shadow: {','.join(shadow_value)};")
        csssetting['recent']['shadow-color'] = shadow_color
    css.append('}')

    for key in ['BEGINNER', 'NORMAL', 'HYPER', 'ANOTHER', 'LEGGENDARIA']:
        color = window[f'recent {key} color'].get()
        if pattern_color.fullmatch(color) is not None:
            window[f'graph recent {key}'].update(background_color=color)
            css.append(f'span.{key} {{ color: {color};}}')
            csssetting['recent'][key] = color

    for key in ['played_count', 'score', 'misscount', 'updated_score', 'updated_misscount', 'clear', 'failed']:
        display = window[f'recent {key} display'].get()
        display_value = 'block' if display else 'none'
        color = window[f'recent {key} color'].get()
        if pattern_color.fullmatch(color) is not None:
            css.append(f'div#{key} {{')
            window[f'graph recent {key} color'].update(background_color=color)
            css.append(f'  display: {display_value};')
            css.append(f'  color: {color};')
            css.append('}')
            csssetting['recent']['overviews'][key]['display'] = display
            csssetting['recent']['overviews'][key]['color'] = color

    window['css'].update('\n'.join(css))

    save_csssetting()

def generate_summary_css(window):
    css = []

    css.append('body {')
    color = window[f'summary color'].get()
    if pattern_color.fullmatch(color) is not None:
        window[f'graph summary color'].update(background_color=color)
        css.append(f'  color: {color};')
        csssetting['summary']['color'] = color
    shadow_color = window[f'summary shadow-color'].get()
    if pattern_color.fullmatch(shadow_color) is not None:
        window[f'graph summary shadow-color'].update(shadow_color)
        shadows = ['1px 1px', '-1px 1px', '1px -1px', '-1px -1px']
        shadow_value = [f'{shadow} 0 {shadow_color}' for shadow in shadows]
        css.append(f"  text-shadow: {','.join(shadow_value)};")
        csssetting['summary']['shadow-color'] = shadow_color
    css.append('}')

    color = window[f'summary date color'].get()
    if pattern_color.fullmatch(color) is not None:
        css.append('div#update_date {')
        window[f'graph summary date color'].update(background_color=color)
        css.append(f'  color: {color};')
        css.append('}')
        csssetting['summary']['date color'] = color

    for play_mode in define.value_list['play_modes']:
        for dj_level in ['A', 'AA', 'AAA']:
            css.append(f"div.{play_mode}.ANOTHER.{dj_level} {{ display: none;}}")
        if window[play_mode].get():
            csssetting['summary'][play_mode]['checked'] = True

            csssetting['summary'][play_mode]['difficulties']['checked'] = []
            for difficulty in define.value_list['difficulties']:
                if window[f'check {play_mode} {difficulty}'].get():
                    csssetting['summary'][play_mode]['difficulties']['checked'].append(difficulty)
                    for clear_type in define.value_list['clear_types']:
                        if window[f'check {play_mode} difficulty {clear_type}'].get():
                            css.append(f"div.{play_mode}.{difficulty}.{clear_type} {{ display: block;}}")
                    for dj_level in define.value_list['dj_levels']:
                        if window[f'check {play_mode} difficulty {dj_level}'].get():
                            css.append(f"div.{play_mode}.{difficulty}.{dj_level} {{ display: block;}}")
            csssetting['summary'][play_mode]['difficulties']['clear_types'] = []
            for clear_type in define.value_list['clear_types']:
                if window[f'check {play_mode} difficulty {clear_type}'].get():
                    csssetting['summary'][play_mode]['difficulties']['clear_types'].append(clear_type)
            csssetting['summary'][play_mode]['difficulties']['dj_levels'] = []
            for dj_level in define.value_list['dj_levels']:
                if window[f'check {play_mode} difficulty {dj_level}'].get():
                    csssetting['summary'][play_mode]['difficulties']['dj_levels'].append(dj_level)

            csssetting['summary'][play_mode]['levels']['checked'] = []
            for level in define.value_list['levels']:
                if window[f'check {play_mode} {level}'].get():
                    csssetting['summary'][play_mode]['levels']['checked'].append(level)
                    for clear_type in define.value_list['clear_types']:
                        if window[f'check {play_mode} level {clear_type}'].get():
                            css.append(f"div.{play_mode}.LEVEL{level}.{clear_type} {{ display: block;}}")
                    for dj_level in define.value_list['dj_levels']:
                        if window[f'check {play_mode} level {dj_level}'].get():
                            css.append(f"div.{play_mode}.LEVEL{level}.{dj_level} {{ display: block;}}")
            csssetting['summary'][play_mode]['levels']['clear_types'] = []
            for clear_type in define.value_list['clear_types']:
                if window[f'check {play_mode} level {clear_type}'].get():
                    csssetting['summary'][play_mode]['levels']['clear_types'].append(clear_type)
            csssetting['summary'][play_mode]['levels']['dj_levels'] = []
            for dj_level in define.value_list['dj_levels']:
                if window[f'check {play_mode} level {dj_level}'].get():
                    csssetting['summary'][play_mode]['levels']['dj_levels'].append(dj_level)
        else:
            csssetting['summary'][play_mode]['checked'] = False

    window['css'].update('\n'.join(css))

    save_csssetting()

def save_csssetting():
    with open(csssetting_filepath, 'w') as f:
        json.dump(csssetting, f, indent=2)
