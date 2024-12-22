from datetime import datetime
from webbrowser import open
from urllib.parse import quote

from define import define
from resources import resource
from record import NotebookSummary
from notesradar import NotesRadar

post_url = 'https://twitter.com/intent/tweet'

def score_format(playmode: str, difficulty: str, musicname: str):
    return ''.join((
        musicname if musicname is not None else '??????',
        '[',
        playmode if playmode is not None else '??',
        difficulty[0] if difficulty is not None else '?',
        ']',
    ))

def timestamp_format(timestamp: str):
    dt = datetime.strptime(timestamp, '%Y%m%d-%H%M%S')
    return datetime.strftime(dt, '%Y/%m/%d %H:%M:%S')

def post_summary(notebook: NotebookSummary, hashtags: str):
    counts = {}
    for playmode in define.value_list['play_modes']:
        counts[playmode] = {'TOTAL': 0, 'F-COMBO': 0, 'AAA': 0, 'NO DATA': 0}
    
    for musicname, value1 in resource.musictable['musics'].items():
        for playmode in define.value_list['play_modes']:
            for difficulty in value1[playmode].keys():
                counts[playmode]['TOTAL'] += 1
                if musicname in notebook.json['musics'].keys() and difficulty in notebook.json['musics'][musicname][playmode].keys():
                    if notebook.json['musics'][musicname][playmode][difficulty]['cleartype'] == 'F-COMBO':
                        counts[playmode]['F-COMBO'] += 1
                    if notebook.json['musics'][musicname][playmode][difficulty]['djlevel'] == 'AAA':
                        counts[playmode]['AAA'] += 1
                else:
                    counts[playmode]['NO DATA'] += 1

    musics_text = []
    for playmode, value in counts.items():
        total = value['TOTAL']
        fullcombo = value['F-COMBO']
        aaa = value['AAA']
        nodata = value['NO DATA']
        musics_text.append(f'{playmode}(全{total}) F-COMBO: {fullcombo} AAA: {aaa}')

    text = quote('\n'.join((*musics_text, hashtags)))
    url = f'{post_url}?text={text}'

    open(url)

def post_notesradar(notesradar: NotesRadar, hashtags: str):
    musics_text = []
    for playmode, item in notesradar.items.items():
        musics_text.append(f'{playmode} TOTAL: {item.total}')
    
    for playmode, item in notesradar.items.items():
        musics_text.append('')
        musics_text.append(playmode)
        for attributekey, attribute in item.attributes.items():
            musics_text.append(f'{attributekey}: {attribute.average}')

    text = quote('\n'.join((*musics_text, hashtags)))
    url = f'{post_url}?text={text}'

    open(url)

def post_results(values: list[dict], hashtags: str):
    musics_text = []
    for result in values:
        music = result['music']
        music = music if music is not None else '??????'

        line = [score_format(result['play_mode'], result['difficulty'], music)]

        if result['update_clear_type'] is not None or result['update_dj_level'] is not None:
            line.append(' '.join(v for v in [result['update_clear_type'], result['update_dj_level']] if v is not None))
        else:
            if result['update_score'] is not None:
                line.append(f"自己ベスト+{result['update_score']}")
            else:
                if result['update_miss_count'] is not None:
                    line.append(f"ミスカウント{result['update_miss_count']}")
                else:
                    line.append('')

        if result['option'] is not None:
            if result['option'] == '':
                line.append('(正規)')
            else:
                line.append(f"({result['option']})")
        else:
            line.append('')

        musics_text.append(''.join(line))

    text = quote('\n'.join((*musics_text, hashtags)))
    url = f'{post_url}?text={text}'

    open(url)

def post_scoreinformation(playmode: str, difficulty: str, musicname: str, record: dict, hashtags: str):
    lines = [score_format(playmode, difficulty, musicname)]

    if 'timestamps' in record.keys():
        lines.append(f"今までプレイ回数: {len(record['timestamps'])} 回")
    
    if 'latest' in record.keys() and 'timestamp' in record['latest'].keys() and record['latest']['timestamp'] is not None:
        lines.append(f"最近のプレイ: {timestamp_format(record['latest']['timestamp'])}")

    if 'best' in record.keys():
        for key, label in [('score', 'スコア'), ('miss_count', 'ミスカウント'),]:
            if key in record['best'].keys() and record['best'][key] is not None:
                if 'timestamp' in record['best'][key].keys() and record['best'][key]['timestamp'] is not None:
                    dt = timestamp_format(record['best'][key]['timestamp'])
                else:
                    dt = '日時不明'
                lines.append(f"{label}: {record['best'][key]['value']}({dt})")

    if 'achievement' in record.keys():
        for key, label in [('fixed', '正規orミラー'), ('S-RANDOM', 'S-RANDOM'),]:
            if key in record['achievement'].keys() and record['achievement'][key] is not None:
                achievements = []
                if record['achievement'][key]['clear_type'] is not None:
                    achievements.append(record['achievement'][key]['clear_type'])
                if record['achievement'][key]['dj_level'] is not None:
                    achievements.append(record['achievement'][key]['dj_level'])
                if len(achievements) > 0:
                    lines.append('')
                    lines.append(f"{label} で {' '.join(achievements)} 達成済み")

    text = quote('\n'.join((*lines, hashtags)))
    url = f'{post_url}?text={text}'

    open(url)
