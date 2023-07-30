import json
from os.path import exists,join
from datetime import datetime
from csv import writer

from define import define
from record import NotebookMusic,get_record_musics,delete_recordfile
from recog import recog
from version import version

export_dirname = 'export'

csssetting_filepath = join(export_dirname, 'css.json')

recent_filepath = join(export_dirname, 'recent.json')
summary_timestamp_filepath = join(export_dirname, 'summary_timestamp.txt')

recent_htmlpath = join(export_dirname, 'recent.html')
summary_htmlpath = join(export_dirname, 'summary.html')

class Recent():
    delete_delta_seconds = 60 * 60 * 12

    def __init__(self):
        if not exists(recent_filepath):
            self.clear()
            return
        
        try:
            with open(recent_filepath) as f:
                self.json = json.load(f)
                if not 'version' in self.json.keys() or self.json['version'] != version:
                    self.clear()
                    self.save()
                    return

                if self.delete_olds() > 0:
                    self.save()
        except Exception:
            self.clear()
    
    def clear(self):
        self.json = {'version': version, 'count': 0, 'score': 0, 'misscount': 0, 'updated_score': 0, 'updated_misscount': 0, 'clear': 0, 'list': []}
        self.save()
    
    def delete_olds(self):
        count = 0
        while len(self.json['list']) != 0:
            target = self.json['list'][0]
            delta = datetime.now() - datetime.strptime(target['timestamp'], '%Y%m%d-%H%M%S')
            if delta.days * 86400 + delta.seconds < self.delete_delta_seconds:
                break

            self.json['count'] -= 1
            self.json['score'] -= target['score']
            self.json['misscount'] -= target['misscount']
            self.json['updated_score'] -= target['updated_score']
            self.json['updated_misscount'] -= target['updated_misscount']
            if target['clear']:
                self.json['clear'] -= 1
            
            del self.json['list'][0]

            count += 1
        return count

    def insert(self, result):
        self.delete_olds()
        
        if result.details.score.best is not None:
            score_diff = result.details.score.current - result.details.score.best
            score_update = score_diff if score_diff > 0 else 0
        else:
            score_update = 0
        if result.details.miss_count.best is not None and result.details.miss_count.current is not None:
            misscount_diff = result.details.miss_count.best - result.details.miss_count.current
            misscount_update = misscount_diff if misscount_diff is not None and misscount_diff > 0 else 0
        else:
            misscount_update = 0

        score = result.details.score.current
        misscount = result.details.miss_count.current if result.details.miss_count.current is not None else 0
        clear = result.details.clear_type.current != 'NO PLAY' and result.details.clear_type.current != 'FAILED'

        self.json['list'].append({
            'timestamp': result.timestamp,
            'difficulty': result.informations.difficulty,
            'music': result.informations.music,
            'new': result.has_new_record(),
            'score': score,
            'misscount': misscount,
            'updated_score': score_update,
            'updated_misscount': misscount_update,
            'clear': clear
        })
        self.json['count'] += 1
        self.json['score'] += score
        self.json['misscount'] += misscount
        self.json['updated_score'] += score_update
        self.json['updated_misscount'] += misscount_update
        if clear:
            self.json['clear'] += 1
        
        self.save()

    def save(self):
        with open(recent_filepath, 'w') as f:
            json.dump(self.json, f)

def output():
    musics_record = get_record_musics()
    musics_all = recog.musictable['musics'].keys()

    summary_filenames = {
        'difficulties': {
            'clear_types': '難易度-クリアタイプ',
            'dj_levels': '難易度-DJレベル'
        },
        'levels': {
            'clear_types': 'レベル-クリアタイプ',
            'dj_levels': 'レベル-DJレベル'
        }
    }

    all_header = ['曲名', '難易度', 'レベル', '最終プレイ日時', 'プレイ回数', 'クリアタイプ', 'DJレベル', 'スコア', 'ミスカウント']

    summary_keys1 = ['difficulties', 'levels']
    summary_keys2 = ['clear_types', 'dj_levels']

    summary = {}
    csv_output = {}
    for play_mode in define.value_list['play_modes']:
        summary[play_mode] = {}
        csv_output[play_mode] = [all_header]
        for summary_key1 in summary_keys1:
            summary[play_mode][summary_key1] = {}
            for key in define.value_list[summary_key1]:
                summary[play_mode][summary_key1][key] = {}
                for summary_key2 in summary_keys2:
                    summary[play_mode][summary_key1][key][summary_key2] = {}
                    for value_key in define.value_list[summary_key2]:
                        summary[play_mode][summary_key1][key][summary_key2][value_key] = 0

    for music in musics_record:
        if not music in musics_all:
            print(f'wrong music: {music}')
            delete_recordfile(music)
            continue
        record = NotebookMusic(music)
        for play_mode in define.value_list['play_modes']:
            for difficulty in define.value_list['difficulties']:
                r = record.get_recordlist(play_mode, difficulty)
                if r is None:
                    continue

                lines = [music, difficulty]
                lines.append(r['level'] if 'level' in r.keys() else '')
                lines.append(r['latest']['timestamp'])
                lines.append(len(r['timestamps']))

                if not 'best' in r.keys():
                    lines.extend(['', '', '', ''])
                    continue

                best = r['best']

                for key in ['clear_type', 'dj_level']:
                    if not key in best:
                        continue
                    
                    if best[key]['value'] is not None:
                        if key == 'clear_type':
                            summary[play_mode]['difficulties'][difficulty]['clear_types'][best[key]['value']] += 1
                        if key == 'dj_level':
                            summary[play_mode]['difficulties'][difficulty]['dj_levels'][best[key]['value']] += 1

                        if 'level' in r.keys():
                            if key == 'clear_type':
                                summary[play_mode]['levels'][r['level']]['clear_types'][best[key]['value']] += 1
                            if key == 'dj_level':
                                summary[play_mode]['levels'][r['level']]['dj_levels'][best[key]['value']] += 1
                    
                for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
                    if not key in best:
                        lines.append('')
                        continue

                    lines.append(best[key]['value'] if best[key]['value'] is not None else '')
                csv_output[play_mode].append(lines)

    for play_mode in define.value_list['play_modes']:
        for summary_key1 in summary_keys1:
            for summary_key2 in summary_keys2:
                lines = [['', *define.value_list[summary_key2], 'total']]
                for key in define.value_list[summary_key1]:
                    targets = summary[play_mode][summary_key1][key][summary_key2].values()
                    lines.append([key,*targets, sum(targets)])
                filepath = join(export_dirname, f'{play_mode}-{summary_filenames[summary_key1][summary_key2]}.csv')
                with open(filepath, 'w', newline='\n') as f:
                    w = writer(f)
                    w.writerows(lines)

    for play_mode in define.value_list['play_modes']:
        filepath = join(export_dirname, f'{play_mode}.csv')
        with open(filepath, 'w', encoding='cp932', newline='\n') as f:
            w = writer(f)
            for line in csv_output[play_mode]:
                try:
                    w.writerow(line)
                except Exception as ex:
                    print('エンコードに失敗', line[0])
    
    with open(summary_timestamp_filepath, 'w') as f:
        f.write(str(datetime.now()))

if __name__ == '__main__':
    output()
