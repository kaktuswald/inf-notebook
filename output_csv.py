from csv import writer

from define import define
from record import Record,get_recode_musics

def output(musics):
    header = ['曲名', '難易度', 'レベル', '最終プレイ日時', 'プレイ回数', 'ベスト クリアタイプ', 'ベスト DJレベル', 'ベスト スコア', 'ベスト ミスカウント']

    values_sp = [header]
    values_dp = [header]
    targets = {
        'SP': values_sp,
        'DP': values_dp
    }
    for music in musics:
        record = Record(music)
        for play_mode in define.value_list['play_modes']:
            target = targets[play_mode]
            for difficulty in define.value_list['difficulties']:
                r = record.get(play_mode, difficulty)
                if r is None:
                    continue
                lines = [music, difficulty]
                lines.append(r['level'] if 'level' in r.keys() else '')
                lines.append(r['latest']['timestamp'])
                lines.append(len(r['timestamps']))
                if 'best' in r.keys():
                    for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
                        if key in r['best']:
                            lines.append(r['best'][key]['value'] if r['best'][key]['value'] is not None else '')
                        else:
                            lines.append('')
                else:
                    lines.extend(['', '', '', ''])
                target.append(lines)

    with open('sp.csv', 'w', encoding='Shift-JIS', newline='\n') as f:
        w = writer(f)
        w.writerows(values_sp)

    with open('dp.csv', 'w', encoding='Shift-JIS', newline='\n') as f:
        w = writer(f)
        w.writerows(values_dp)

if __name__ == '__main__':
    musics = get_recode_musics()
    output(musics)