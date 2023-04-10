import json
from os.path import exists,join
from datetime import datetime
from csv import writer

from define import define
from record import Record,get_record_musics

export_dirname = 'export'

recent_filepath = join(export_dirname, 'recent.json')
summary_filepath = join(export_dirname, 'summary.json')

class Recent():
    delete_delta_seconds = 60 * 60 * 12

    def __init__(self):
        if not exists(recent_filepath):
            self.json = []
            return
        
        try:
            with open(recent_filepath) as f:
                self.json = json.load(f)
                if self.delete_olds() > 0:
                    self.save()
        except Exception:
            self.json = []
    
    def delete_olds(self):
        count = 0
        while len(self.json) != 0:
            delta = datetime.now() - datetime.strptime(self.json[0]['timestamp'], '%Y%m%d-%H%M%S')
            if delta.seconds < self.delete_delta_seconds:
                break
            del self.json[0]
            count += 1
        return count

    def insert(self, result):
        self.delete_olds()
        self.json.append({
            'timestamp': result.timestamp,
            'music': result.informations.music,
            'new': result.has_new_record()
        })
        self.save()

    def save(self):
        with open(recent_filepath, 'w') as f:
            json.dump(self.json, f)

def output():
    musics = get_record_musics()

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

    for music in musics:
        record = Record(music)
        for play_mode in define.value_list['play_modes']:
            for difficulty in define.value_list['difficulties']:
                r = record.get(play_mode, difficulty)
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
                lines = [['', *define.value_list[summary_key2]]]
                for key in define.value_list[summary_key1]:
                    lines.append([key, *summary[play_mode][summary_key1][key][summary_key2].values()])
                filepath = join(export_dirname, f'{play_mode}-{summary_filenames[summary_key1][summary_key2]}.csv')
                with open(filepath, 'w', newline='\n') as f:
                    w = writer(f)
                    w.writerows(lines)

    for play_mode in define.value_list['play_modes']:
        filepath = join(export_dirname, f'{play_mode}.csv')
        with open(filepath, 'w', encoding='Shift-JIS', newline='\n') as f:
            w = writer(f)
            w.writerows(csv_output[play_mode])

if __name__ == '__main__':
    output()