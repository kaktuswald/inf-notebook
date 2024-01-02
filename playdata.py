import json
from os.path import exists,join
from datetime import datetime
from csv import writer
from logging import getLogger

logger_child_name = 'resources'

logger = getLogger().getChild(logger_child_name)
logger.debug(f'loaded resources.py')

from define import define
from resources import resource
from record import NotebookMusic
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

    all_header = ['バージョン', '曲名', '難易度', 'レベル', '最終プレイ日時', 'プレイ回数', 'クリアタイプ', 'DJレベル', 'スコア', 'ミスカウント']

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
                    for value_key in [*define.value_list[summary_key2], 'TOTAL']:
                        summary[play_mode][summary_key1][key][summary_key2][value_key] = 0

    for music, music_item in resource.musictable['musics'].items():
        version = music_item['version']
        record = NotebookMusic(music)
        for play_mode in define.value_list['play_modes']:
            for difficulty in define.value_list['difficulties']:
                if not difficulty in music_item[play_mode].keys() or music_item[play_mode][difficulty] is None:
                    continue

                level = music_item[play_mode][difficulty]

                summary[play_mode]['difficulties'][difficulty]['clear_types']['TOTAL'] += 1
                summary[play_mode]['difficulties'][difficulty]['dj_levels']['TOTAL'] += 1
                summary[play_mode]['levels'][level]['clear_types']['TOTAL'] += 1
                summary[play_mode]['levels'][level]['dj_levels']['TOTAL'] += 1

                lines = [version, music, difficulty, level]

                r = record.get_recordlist(play_mode, difficulty)
                if r is not None:
                    lines.append(r['latest']['timestamp'] if 'latest' in r.keys() else '')
                    lines.append(len(r['timestamps']) if 'timestamps' in r.keys() else '')

                    if 'best' in r.keys():
                        best = r['best']

                        for key in ['clear_type', 'dj_level']:
                            if key in best.keys() and best[key] is not None and best[key]['value'] is not None:
                                if key == 'clear_type':
                                    summary[play_mode]['difficulties'][difficulty]['clear_types'][best[key]['value']] += 1
                                if key == 'dj_level':
                                    summary[play_mode]['difficulties'][difficulty]['dj_levels'][best[key]['value']] += 1

                                level = music_item[play_mode][difficulty]
                                if key == 'clear_type':
                                    summary[play_mode]['levels'][level]['clear_types'][best[key]['value']] += 1
                                if key == 'dj_level':
                                    summary[play_mode]['levels'][level]['dj_levels'][best[key]['value']] += 1
                            
                        for key in ['clear_type', 'dj_level', 'score', 'miss_count']:
                            if key in best.keys() and best[key] is not None and 'value' in best[key].keys():
                                lines.append(best[key]['value'] if best[key]['value'] is not None else '')
                            else:
                                lines.append('')
                    else:
                        lines.extend(['', '', '', ''])
                else:
                    lines.extend(['', '', '', '', '', ''])

                csv_output[play_mode].append(lines)

    for play_mode in define.value_list['play_modes']:
        for summary_key1 in summary_keys1:
            for summary_key2 in summary_keys2:
                lines = [['', *define.value_list[summary_key2], 'NO DATA', 'TOTAL']]
                for key in define.value_list[summary_key1]:
                    total_count = summary[play_mode][summary_key1][key][summary_key2]['TOTAL']
                    targets = [*summary[play_mode][summary_key1][key][summary_key2].values()][:-1]
                    no_data_count = total_count - sum(targets)
                    lines.append([key, *targets, no_data_count, total_count])
                filepath = join(export_dirname, f'{play_mode}-{summary_filenames[summary_key1][summary_key2]}.csv')
                with open(filepath, 'w', newline='\n') as f:
                    w = writer(f)
                    w.writerows(lines)

    for play_mode in define.value_list['play_modes']:
        filepath = join(export_dirname, f'{play_mode}.csv')
        with open(filepath, 'w', encoding='UTF-8', newline='\n') as f:
            w = writer(f)
            for line in csv_output[play_mode]:
                try:
                    w.writerow(line)
                except Exception as ex:
                    logger.debug('エンコードに失敗', line[0])
                    logger.debug(ex)
    
    with open(summary_timestamp_filepath, 'w') as f:
        f.write(str(datetime.now()))

if __name__ == '__main__':
    output()
