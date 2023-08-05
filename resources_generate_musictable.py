from os.path import join

from define import define
from resources_generate import Report

scoredata_sp_filename = 'score_data_sp.csv'
scoredata_dp_filename = 'score_data_dp.csv'
musiclist_filepath = 'musics.csv'

def load_musiclist(report):
    with open(musiclist_filepath, 'r', encoding='utf-8') as f:
        musiclist = f.read().split('\n')

    versions = {}
    musics = {}
    for line in musiclist:
        if len(line) == 0:
            continue
        
        values = line.split(',')
        values = [values[0], ','.join(values[1:-10]), *values[-10:]]

        version = values[0]
        if not version in versions.keys():
            versions[version] = []

        music = values[1]
        if music == '':
            report.error(f'Music blank error: {line}')
        
        versions[version].append(music)
        musics[music] = {'version': version}
        for play_mode in define.value_list['play_modes']:
            musics[music][play_mode] = {}
    
        index = 2
        for play_mode in define.value_list['play_modes']:
            for difficulty in define.value_list['difficulties']:
                if values[index] != '-':
                    musics[music][play_mode][difficulty] = values[index] if values[index] != '0' else None
                index += 1

    versions['Unknown'] = []

    return versions, musics

def reflect_collections_analyzed(report, versions, musics, analyzed):
    for music in analyzed.keys():
        version = 'Unknown'
        for key, value in versions.items():
            if music in value:
                version = key
                break

        if version == 'Unknown':
            versions[version].append(music)
            musics[music] = {'version': 'Unknown'}
            for play_mode in define.value_list['play_modes']:
                musics[music][play_mode] = {}
        
        for play_mode in analyzed[music].keys():
            for difficulty, value in analyzed[music][play_mode].items():
                if difficulty in musics[music][play_mode].keys() and value != musics[music][play_mode][difficulty]:
                    report.error(f"Mismatch {version} {music} {play_mode} {difficulty}: {value}, {musics[music][play_mode][difficulty]}")
                else:
                    musics[music][play_mode][difficulty] = value

def reflect_scoredata(versions, musics, play_mode, filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        scoredata = f.read().split('\n')

    for line in scoredata[1:-1]:
        values = line.split(',')
        values = [values[0], ','.join(values[1:-39]), *values[-39:]]

        version = values[0]
        if not version in versions.keys():
            continue

        music = values[1]
        if not music in musics.keys():
            continue

        if values[5] != '0' and not 'BEGGINER' in musics[music][play_mode].keys():
            musics[music][play_mode]['BEGINNER'] = values[5]
        if values[12] != '0' and not 'NORMAL' in musics[music][play_mode].keys():
            musics[music][play_mode]['NORMAL'] = values[12]
        if values[19] != '0' and not 'HYPER' in musics[music][play_mode].keys():
            musics[music][play_mode]['HYPER'] = values[19]
        if values[26] != '0' and not 'ANOTHER' in musics[music][play_mode].keys():
            musics[music][play_mode]['ANOTHER'] = values[26]
        if values[33] != '0' and not 'LEGGENDARIA' in musics[music][play_mode].keys():
            musics[music][play_mode]['LEGGENDARIA'] = values[33]

def generate(analyzed, reportdir):
    report = Report('musictable')

    versions, musics = load_musiclist(report)

    reflect_collections_analyzed(report, versions, musics, analyzed)

    reflect_scoredata(versions, musics, 'SP', scoredata_sp_filename)
    reflect_scoredata(versions, musics, 'DP', scoredata_dp_filename)

    report.append_log(f'Total count: {len(musics)}')
    report.append_log('')

    report_versions = []
    report.append_log('Number of musics in each version.')
    for version in versions.keys():
        report.append_log(f'{version}: {len(versions[version])}')
        report_versions.append(f'{version}: {len(versions[version])}')
        for music in versions[version]:
            levels = []
            for play_mode in define.value_list['play_modes']:
                for difficulty in define.value_list['difficulties']:
                    if difficulty in musics[music][play_mode].keys() and musics[music][play_mode][difficulty] is not None:
                        levels.append(f'{play_mode}{difficulty[0]}{musics[music][play_mode][difficulty]}')
            report_versions.append(f"  {music}: {' '.join(levels)}")
    report.append_log('')

    report_filepath = join(reportdir, 'musictable_versions.txt')
    with open(report_filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_versions))

    leggendarias = {}
    for play_mode in define.value_list['play_modes']:
        leggendarias[play_mode] = {}
        for music in musics.keys():
            if 'LEGGENDARIA' in musics[music][play_mode].keys() and musics[music][play_mode]['LEGGENDARIA'] is not None:
                leggendarias[play_mode][music] = musics[music][play_mode]['LEGGENDARIA']

    report_leggendarias = []
    for play_mode in define.value_list['play_modes']:
        report_leggendarias.append(f'{play_mode}: {len(leggendarias[play_mode])}')
        report_leggendarias.extend([f'  {key}: {value}' for key, value in leggendarias[play_mode].items()])

    report_filepath = join(reportdir, 'musictable_leggendarias.txt')
    with open(report_filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_leggendarias))

    levels = {}
    for play_mode in define.value_list['play_modes']:
        levels[play_mode] = {}
        for level in define.value_list['levels']:
            levels[play_mode][level] = []
        for music in musics.keys():
            for difficulty in define.value_list['difficulties']:
                if difficulty in musics[music][play_mode].keys() and musics[music][play_mode][difficulty] != None:
                    level = musics[music][play_mode][difficulty]
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
        'musics': musics,
        'versions': versions,
        'levels': levels,
    }
