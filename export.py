import json
from os.path import exists,join
from datetime import datetime
from csv import writer
from decimal import Decimal
import re
from dataclasses import dataclass
from logging import getLogger

if __name__ == '__main__':
    logger = getLogger()
else:
    logger = getLogger(__name__)
logger.debug(f'loaded {logger.name}')

from define import Playmodes,Playtypes,define
from resources import resource
from record import NotebookSummary
from notesradar import NotesRadar
from version import version

export_dirname = 'export'

csssetting_filepath = join(export_dirname, 'css.json')

recent_filepath = join(export_dirname, 'recent.json')
summary_timestamp_filepath = join(export_dirname, 'summary_timestamp.txt')

recent_htmlpath = join(export_dirname, 'recent.html')
summary_htmlpath = join(export_dirname, 'summary.html')

notesradar_csv_filepath = join(export_dirname, 'notesradar.csv')
notesradar_csv_rankings_filepaths = {
    Playmodes.SP: join(export_dirname, 'notesradar_rankings_sp.csv'),
    Playmodes.DP: join(export_dirname, 'notesradar_rankings_dp.csv')
}

settingcss_filepath = join(export_dirname, 'setting.css')

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
        if result.details.misscount.best is not None and result.details.misscount.current is not None:
            misscount_diff = result.details.misscount.best - result.details.misscount.current
            misscount_update = misscount_diff if misscount_diff is not None and misscount_diff > 0 else 0
        else:
            misscount_update = 0

        score = result.details.score.current
        misscount = result.details.misscount.current if result.details.misscount.current is not None else 0
        clear = result.details.cleartype.current != 'NO PLAY' and result.details.cleartype.current != 'FAILED'

        self.json['list'].append({
            'timestamp': result.timestamp,
            'difficulty': result.informations.difficulty,
            'music': result.informations.songname,
            'new': result.has_newrecord,
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

class CsvRowData:
    @dataclass
    class Best:
        value: str|int|None = None
        option: str|None = None
    
    @dataclass
    class Achievement:
        mixture: str|None = None
        ''' MAX or F-COMBO & AAA'''
        cleartype: str|None = None
        djlevel: str|None = None

    version: str
    songname: str
    difficulty: str
    level: int
    latest: str|None
    playcount: int|None
    best_cleartype: Best
    best_djlevel: Best
    best_score: Best
    best_misscount: Best
    achievement_fixed: Achievement
    achievement_srandom: Achievement
    achievement_allscratch: Achievement
    notes: int|None
    notesradar_attribute: str|None

    COLUMNS = [
        'バージョン',
        '曲名',
        '難易度',
        'レベル',
        '最終プレイ日時',
        'プレイ回数',
        'クリアタイプ',
        'クリアタイプ更新オプション',
        'DJレベル',
        'DJレベル更新オプション',
        'スコア',
        'スコア更新オプション',
        'ミスカウント',
        'ミスカウント更新オプション',
        '固定配置実績',
        '固定配置クリアタイプ',
        '固定配置DJレベル',
        'S-RANDOM実績',
        'S-RANDOMクリアタイプ',
        'S-RANDOMDJレベル',
        'ALL-SCR実績',
        'ALL-SCRクリアタイプ',
        'ALL-SCRDJレベル',
        'ノーツ数',
        'ノーツレーダー属性',
    ]

    def __init__(self, **kwargs):
        self.version = kwargs.get('version')
        self.songname = kwargs.get('songname')
        self.difficulty = kwargs.get('difficulty')
        self.level = kwargs.get('level')
        self.latest = None
        self.playcount = None
        self.best_cleartype = CsvRowData.Best()
        self.best_djlevel = CsvRowData.Best()
        self.best_score = CsvRowData.Best()
        self.best_misscount = CsvRowData.Best()
        self.achievement_fixed = CsvRowData.Achievement()
        self.achievement_srandom = CsvRowData.Achievement()
        self.achievement_allscratch = CsvRowData.Achievement()
        self.notes = None
        self.notesradar_attribute = None

    def expand(self) -> list[str]:
        return [
            self.version,
            self.songname,
            self.difficulty,
            self.level,
            self.latest,
            self.playcount,
            self.best_cleartype.value,
            self.best_cleartype.option,
            self.best_djlevel.value,
            self.best_djlevel.option,
            self.best_score.value,
            self.best_score.option,
            self.best_misscount.value,
            self.best_misscount.option,
            self.achievement_fixed.mixture,
            self.achievement_fixed.cleartype,
            self.achievement_fixed.djlevel,
            self.achievement_srandom.mixture,
            self.achievement_srandom.cleartype,
            self.achievement_srandom.djlevel,
            self.achievement_allscratch.mixture,
            self.achievement_allscratch.cleartype,
            self.achievement_allscratch.djlevel,
            self.notes,
            self.notesradar_attribute,
        ]

def output(notebook: NotebookSummary):
    '''CSVファイルを出力する
    
    Args:
        notebook (NotebookSummary): 対象のデータ
    '''
    musictable = resource.musictable
    notesradar = resource.notesradar

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

    summary_keys1 = ['difficulties', 'levels']
    summary_keys2 = ['clear_types', 'dj_levels']

    summary = {}
    csv_output: dict[str, list[CsvRowData]] = {}
    for playtype in Playtypes.values:
        summary[playtype] = {}
        csv_output[playtype] = []
        for summary_key1 in summary_keys1:
            summary[playtype][summary_key1] = {}
            for key in define.value_list[summary_key1]:
                summary[playtype][summary_key1][key] = {}
                for summary_key2 in summary_keys2:
                    summary[playtype][summary_key1][key][summary_key2] = {}
                    for value_key in [*define.value_list[summary_key2], 'TOTAL']:
                        summary[playtype][summary_key1][key][summary_key2][value_key] = 0
    
    for musicname, music_item in musictable['musics'].items():
        version = music_item['version']
        if 'musics' in notebook.json.keys() and musicname in notebook.json['musics'].keys():
            notebook_target = notebook.json['musics'][musicname]
        else:
            notebook_target = None
        for playtype in Playtypes.values:
            for difficulty in define.value_list['difficulties']:
                playmode = 'SP' if playtype in ('SP', 'DP BATTLE', ) else 'DP'
                if not difficulty in music_item[playmode].keys() or music_item[playmode][difficulty] is None:
                    continue

                level = music_item[playmode][difficulty]

                summary[playtype]['difficulties'][difficulty]['clear_types']['TOTAL'] += 1
                summary[playtype]['difficulties'][difficulty]['dj_levels']['TOTAL'] += 1
                summary[playtype]['levels'][level]['clear_types']['TOTAL'] += 1
                summary[playtype]['levels'][level]['dj_levels']['TOTAL'] += 1

                rowdata = CsvRowData(version=version, songname=musicname, difficulty=difficulty, level=level)

                if notebook_target and playtype in notebook_target.keys() and difficulty in notebook_target[playtype].keys():
                    record = notebook_target[playtype][difficulty]

                    rowdata.latest = record.get('latest') or None
                    rowdata.playcount = record.get('playcount') or 0

                    if 'best' in record.keys() and record['best'] is not None:
                        besttargets: dict[str, CsvRowData.Best] = {
                            'cleartype': rowdata.best_cleartype,
                            'djlevel': rowdata.best_djlevel,
                            'score': rowdata.best_score,
                            'misscount': rowdata.best_misscount,
                        }
                        for key, target in besttargets.items():
                            if record['best'][key] is not None:
                                target.value = record['best'][key]['value'] if record['best'][key]['value'] is not None else ''

                                option = None
                                if 'options' in record['best'][key].keys() and record['best'][key]['options'] is not None:
                                    optionvalues = [
                                        record['best'][key]['options']['arrange'],
                                        record['best'][key]['options']['flip'],
                                        record['best'][key]['options']['assist'],
                                    ]
                                    option = ','.join([v for v in optionvalues if v is not None])
                                    if option == '':
                                        option = '---'
                                target.option = option or '???'

                        if record['best']['cleartype'] is not None:
                            value = record['best']['cleartype']['value']
                            summary[playtype]['difficulties'][difficulty]['clear_types'][value] += 1
                            summary[playtype]['levels'][level]['clear_types'][value] += 1
                        
                        if record['best']['djlevel'] is not None:
                            value = record['best']['djlevel']['value']
                            summary[playtype]['difficulties'][difficulty]['dj_levels'][value] += 1
                            summary[playtype]['levels'][level]['dj_levels'][value] += 1
                    
                    if 'achievement' in record.keys() and record['achievement'] is not None:
                        achievementtargets: dict[str, CsvRowData.Achievement] = {
                            'fixed': rowdata.achievement_fixed,
                            'S-RANDOM': rowdata.achievement_srandom,
                            'ALL-SCR': rowdata.achievement_allscratch,
                        }
                        for key1, target in achievementtargets.items():
                            if key1 in record['achievement'].keys():
                                if 'MAX' in record['achievement'][key1].keys() or 'F-COMBO & AAA' in record['achievement'][key1].keys():
                                    if 'MAX' in record['achievement'][key1].keys():
                                        target.mixture = 'MAX'
                                    else:
                                        target.mixture = 'F-COMBO & AAA'

                                if key1 in record['achievement'].keys():
                                    target.cleartype = record['achievement'][key1]['clear_type'] or ''
                                    target.djlevel = record['achievement'][key1]['dj_level'] or ''
                
                if musicname in notesradar[playmode]['musics'].keys() and difficulty in notesradar[playmode]['musics'][musicname].keys():
                    rowdata.notes = notesradar[playmode]['musics'][musicname][difficulty]['notes']
                    rowdata.notesradar_attribute = '/'.join(notesradar[playmode]['musics'][musicname][difficulty]['attributes'])
                
                csv_output[playtype].append(rowdata)

    for playtype in Playtypes.values:
        for summary_key1 in summary_keys1:
            for summary_key2 in summary_keys2:
                lines = [['', *define.value_list[summary_key2], 'NO DATA', 'TOTAL']]
                for key in define.value_list[summary_key1]:
                    total_count = summary[playtype][summary_key1][key][summary_key2]['TOTAL']
                    targets = [*summary[playtype][summary_key1][key][summary_key2].values()][:-1]
                    no_data_count = total_count - sum(targets)
                    lines.append([key, *targets, no_data_count, total_count])
                filepath = join(export_dirname, f'{playtype}-{summary_filenames[summary_key1][summary_key2]}.csv')
                with open(filepath, 'w', newline='\n') as f:
                    w = writer(f)
                    w.writerows(lines)

    for playtype in Playtypes.values:
        filepath = join(export_dirname, f'{playtype}.csv')
        try:
            with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
                w = writer(f)
                w.writerow(CsvRowData.COLUMNS)

                for line in csv_output[playtype]:
                    w.writerow(line.expand())
        except Exception as ex:
            logger.exception(f'エンコードに失敗: {line}')
            logger.exception(ex)
    
    with open(summary_timestamp_filepath, 'w') as f:
        f.write(str(datetime.now()))

def output_notesradarcsv(notesradar: NotesRadar):
    output: list[str] = []
    output_rankings: dict[str, list[str]] = {}
    for playmode, targetitem in notesradar.items.items():
        output.append(playmode)
        output_rankings[playmode] = []
        for attribute, targetattribute in targetitem.attributes.items():
            output.append(f'{attribute}, {targetattribute.average}')
            
            output_rankings[playmode].append(f'順位,曲名,譜面,{attribute},MAX,%')
            for i in range(len(targetattribute.ranking)):
                t = targetattribute.ranking[i]
                max = Decimal(str(resource.notesradar[playmode]['musics'][t.musicname][t.difficulty]['radars'][attribute]))
                
                if max:
                    rate = (t.value/max*Decimal('100.0')).quantize(Decimal('0.00'))
                else:
                    rate = Decimal('0.00')
                
                output_rankings[playmode].append(','.join([
                    str(i + 1),
                    t.musicname,
                    t.difficulty,
                    str(t.value),
                    str(max),
                    str(rate),
                ]))
            output_rankings[playmode].append('')
        output.append('')
    
    with open(notesradar_csv_filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))

    for playmode, item in output_rankings.items():
        with open(notesradar_csv_rankings_filepaths[playmode], 'w', encoding='utf-8') as f:
            f.write('\n'.join(item))

def generate_exportsettingcss(port: int):
    domain = 'localhost'

    if exists(settingcss_filepath):
        with open(settingcss_filepath, 'r', encoding='utf-8') as f:
            css_content = f.read()

            pattern_url = r'\:root\s*{[^}]*--ws-url:\s*([^;]+);'
            pattern_domain = r'\ws://([^:/]+)'
            urlresult = re.search(pattern_url, css_content)
            if urlresult:
                domainresult = re.search(pattern_domain, urlresult.group(1))
                if domainresult:
                    domain = domainresult.group(1)
    
    with open(settingcss_filepath, 'w', encoding='utf-8') as f:
        f.write(':root {\n')
        f.write(f'    --ws-url: ws://{domain}:{port};\n')
        f.write('}\n')
        f.write('')

if __name__ == '__main__':
    notebook = NotebookSummary()
    output(notebook)
