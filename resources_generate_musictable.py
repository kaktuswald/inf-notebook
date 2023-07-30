from os.path import join

from define import define
from resources_generate import Report

scoredata_sp_filename = 'score_data_sp.csv'
scoredata_dp_filename = 'score_data_dp.csv'
musiclist_filepath = 'musics.csv'

def load_musiclist(report):
    with open(musiclist_filepath, 'r', encoding='utf-8') as f:
        musiclist = f.read().split('\n')

    table = {}
    for line in musiclist:
        if len(line) == 0:
            continue
        
        values = line.split(',')
        values = [values[0], ','.join(values[1:-10]), *values[-10:]]

        version = values[0]
        if not version in table.keys():
            table[version] = {}

        music = values[1]
        if music == '':
            report.error(f'Music blank error: {line}')
        
        table[version][music] = {}
        for play_mode in define.value_list['play_modes']:
            table[version][music][play_mode] = {}
    
        if values[2] != '-':
            table[version][music]['SP']['BEGINNER'] = values[2] if values[2] != '0' else None
        if values[3] != '-':
            table[version][music]['SP']['NORMAL'] = values[3] if values[3] != '0' else None
        if values[4] != '-':
            table[version][music]['SP']['HYPER'] = values[4] if values[4] != '0' else None
        if values[5] != '-':
            table[version][music]['SP']['ANOTHER'] = values[5] if values[5] != '0' else None
        if values[6] != '-':
            table[version][music]['SP']['LEGGENDARIA'] = values[6] if values[6] != '0' else None
        if values[7] != '-':
            table[version][music]['DP']['BEGINNER'] = values[7] if values[7] != '0' else None
        if values[8] != '-':
            table[version][music]['DP']['NORMAL'] = values[8] if values[8] != '0' else None
        if values[9] != '-':
            table[version][music]['DP']['HYPER'] = values[9] if values[9] != '0' else None
        if values[10] != '-':
            table[version][music]['DP']['ANOTHER'] = values[10] if values[10] != '0' else None
        if values[11] != '-':
            table[version][music]['DP']['LEGGENDARIA'] = values[11] if values[11] != '0' else None

    table['Unknown'] = {}

    return table

def reflect_collections_analyzed(report, table, analyzed):
    for music in analyzed.keys():
        version = 'Unknown'
        for v, i in table.items():
            if music in i.keys():
                version = v
                break

        if version == 'Unknown':
            table[version][music] = {}
            for play_mode in define.value_list['play_modes']:
                table[version][music][play_mode] = {}

        for play_mode in analyzed[music].keys():
            for difficulty, value in analyzed[music][play_mode].items():
                if value is not None:
                    if difficulty in table[version][music][play_mode].keys() and value != table[version][music][play_mode][difficulty]:
                        report.error(f"Mismatch {version} {music} {play_mode} {difficulty}: {value}, {table[version][music][play_mode][difficulty]}")
                    else:
                        table[version][music][play_mode][difficulty] = value

def reflect_scoredata(table, play_mode, filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        scoredata = f.read().split('\n')

    for line in scoredata[1:-1]:
        values = line.split(',')
        values = [values[0], ','.join(values[1:-39]), *values[-39:]]

        version = values[0]
        if not version in table.keys():
            continue

        music = values[1]
        if not music in table[version].keys():
            continue

        if values[5] != '0' and not 'BEGGINER' in table[version][music][play_mode].keys():
            table[version][music][play_mode]['BEGINNER'] = values[5]
        if values[12] != '0' and not 'NORMAL' in table[version][music][play_mode].keys():
            table[version][music][play_mode]['NORMAL'] = values[12]
        if values[19] != '0' and not 'HYPER' in table[version][music][play_mode].keys():
            table[version][music][play_mode]['HYPER'] = values[19]
        if values[26] != '0' and not 'ANOTHER' in table[version][music][play_mode].keys():
            table[version][music][play_mode]['ANOTHER'] = values[26]
        if values[33] != '0' and not 'LEGGENDARIA' in table[version][music][play_mode].keys():
            table[version][music][play_mode]['LEGGENDARIA'] = values[33]

def generate(analyzed, reportdir):
    report = Report('musictable')

    table = load_musiclist(report)

    reflect_collections_analyzed(report, table, analyzed)

    reflect_scoredata(table, 'SP', scoredata_sp_filename)
    reflect_scoredata(table, 'DP', scoredata_dp_filename)

    report.append_log(f'Total count: {sum([len(musics) for musics in table.values()])}')
    report.append_log('')
    
    versions = {}
    report_versions = []
    report.append_log('Number of musics in each version.')
    for version in table.keys():
        versions[version] = []
        report.append_log(f'{version}: {len(table[version])}')
        report_versions.append(f'{version}: {len(table[version])}')
        for music in table[version].keys():
            report_versions.append(f'  {music}')
    report.append_log('')

    report_filepath = join(reportdir, 'musictable_versions.txt')
    with open(report_filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_versions))

    levels = {}
    for play_mode in define.value_list['play_modes']:
        levels[play_mode] = {}
        for level in define.value_list['levels']:
            levels[play_mode][level] = []
        for version in table.keys():
            for music in table[version].keys():
                for difficulty in define.value_list['difficulties']:
                    if difficulty in table[version][music][play_mode].keys() and table[version][music][play_mode][difficulty] is not None:
                        level = table[version][music][play_mode][difficulty]
                        try:
                            levels[play_mode][level].append({'music': music, 'difficulty': difficulty})
                        except Exception as ex:
                            report.error(f'Musics error?? {music}')

    report_levels = []
    report.append_log('Number of musics in each difficulty.')
    for play_mode in define.value_list['play_modes']:
        for level in define.value_list['levels']:
            report.append_log(f'{play_mode} level {level}: {len(levels[play_mode][level])}')
            report_levels.append(f'{play_mode} level {level}: {len(levels[play_mode][level])}')
            for values in levels[play_mode][level]:
                report_levels.append(f"  {values['music']} {values['difficulty']}")
        report.append_log('')

    report_filepath = join(reportdir, 'musictable_levels.txt')
    with open(report_filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_levels))

    report.report()
    
    return {
        # 'musics': musics,
        'versions': versions,
        'levels': levels,
    }
