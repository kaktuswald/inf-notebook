from datetime import datetime
from webbrowser import open
from urllib.parse import quote

post_url = 'https://twitter.com/intent/tweet'
hashtag = '#IIDX #infinitas573 #infnotebook'

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

def post_results(values: list[dict]):
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

    text = quote('\n'.join((*musics_text, hashtag)))
    url = f'{post_url}?text={text}'

    open(url)

def post_scoreinformation(playmode: str, difficulty: str, musicname: str, record: dict):
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

    text = quote('\n'.join((*lines, hashtag)))
    url = f'{post_url}?text={text}'

    open(url)
